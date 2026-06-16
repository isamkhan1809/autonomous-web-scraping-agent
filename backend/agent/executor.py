import os
import asyncio
from typing import Any
import anthropic

from .browser import BrowserController
from .tools import BROWSER_TOOLS

SYSTEM_PROMPT = """You are an autonomous web scraping agent. Given a goal, you plan and execute browser actions step by step.

Use the available tools to navigate websites, search for information, and extract data. Be methodical:
1. Start by searching Google if you need to find something
2. Navigate to the most relevant result
3. Extract the specific data requested
4. Verify the data looks correct
5. When you have a complete answer, call the finish tool

Always prefer direct navigation when you know the URL. Use search_google when you need to discover URLs.
When extracting data, get_page_content first, then use extract_data to summarize what you found.
Be concise and efficient — do not repeat steps unnecessarily."""


class WebScrapingAgent:
    def __init__(self, anthropic_api_key: str):
        self.client = anthropic.Anthropic(api_key=anthropic_api_key)
        self.browser: BrowserController | None = None

    async def _execute_tool(self, tool_name: str, tool_input: dict, screenshots: list[str]) -> Any:
        """Execute a browser tool and return the result."""
        try:
            if tool_name == "navigate":
                result = await self.browser.navigate(tool_input["url"])
                shot = await self.browser.screenshot()
                if shot:
                    screenshots.append(shot)
                return result

            elif tool_name == "get_page_content":
                text = await self.browser.get_page_text()
                links = await self.browser.get_page_links()
                return {
                    "text": text,
                    "links": links[:20],
                    "link_count": len(links)
                }

            elif tool_name == "search_google":
                results = await self.browser.search_google(tool_input["query"])
                shot = await self.browser.screenshot()
                if shot:
                    screenshots.append(shot)
                return {"results": results, "count": len(results)}

            elif tool_name == "click_link":
                url = tool_input.get("url")
                link_text = tool_input.get("link_text")
                if url:
                    result = await self.browser.navigate(url)
                elif link_text:
                    # Try to find and click by text
                    click_result = await self.browser.click(f"text={link_text}")
                    if not click_result["success"]:
                        return {"success": False, "error": f"Could not find link with text: {link_text}"}
                    await asyncio.sleep(1)
                    result = {"success": True, "url": self.browser._page.url}
                else:
                    return {"success": False, "error": "Must provide either url or link_text"}
                shot = await self.browser.screenshot()
                if shot:
                    screenshots.append(shot)
                return result

            elif tool_name == "extract_data":
                text = await self.browser.get_page_text()
                links = await self.browser.get_page_links()
                desc = tool_input.get("data_description", "all data")
                # Return the raw content so Claude can extract what it needs
                return {
                    "description": desc,
                    "page_text": text,
                    "links": [l for l in links[:10] if l.get("text")],
                    "current_url": self.browser._page.url if self.browser._page else "unknown"
                }

            elif tool_name == "finish":
                return {"done": True, "result": tool_input.get("result", ""), "data": tool_input.get("data")}

            else:
                return {"error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            return {"error": str(e)}

    async def run(self, goal: str, max_steps: int = 15) -> dict:
        self.browser = BrowserController()
        await self.browser.init()

        steps = []
        screenshots: list[str] = []
        messages = [{"role": "user", "content": goal}]
        final_result = None
        success = False
        step_num = 0

        try:
            while step_num < max_steps:
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=4096,
                    system=SYSTEM_PROMPT,
                    tools=BROWSER_TOOLS,
                    messages=messages,
                )

                # Collect assistant message content
                assistant_content = response.content
                messages.append({"role": "assistant", "content": assistant_content})

                # Extract text thought if any
                thought = ""
                for block in assistant_content:
                    if hasattr(block, "type") and block.type == "text":
                        thought = block.text

                # Check stop reason
                if response.stop_reason == "end_turn":
                    # No tool calls — agent finished without calling finish
                    if thought:
                        final_result = thought
                    success = True
                    break

                # Find tool use blocks
                tool_use_blocks = [b for b in assistant_content if hasattr(b, "type") and b.type == "tool_use"]

                if not tool_use_blocks:
                    if thought:
                        final_result = thought
                    success = True
                    break

                # Execute each tool call
                tool_results = []
                for tool_block in tool_use_blocks:
                    step_num += 1
                    tool_name = tool_block.name
                    tool_input = tool_block.input
                    tool_use_id = tool_block.id

                    output = await self._execute_tool(tool_name, tool_input, screenshots)

                    # Record step
                    output_snippet = str(output)
                    if len(output_snippet) > 500:
                        output_snippet = output_snippet[:500] + "..."

                    steps.append({
                        "step_num": step_num,
                        "tool": tool_name,
                        "input": tool_input,
                        "output": output_snippet,
                        "thought": thought,
                    })

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": str(output),
                    })

                    # Check if this was a finish call
                    if tool_name == "finish":
                        final_result = tool_input.get("result", "")
                        success = True
                        break

                if success:
                    break

                # Append tool results
                messages.append({"role": "user", "content": tool_results})

        except Exception as e:
            final_result = f"Agent encountered an error: {str(e)}"
            success = False
        finally:
            await self.browser.close()

        return {
            "goal": goal,
            "steps": steps,
            "result": final_result or "Agent did not produce a final result.",
            "success": success,
            "total_steps": step_num,
            "screenshots": screenshots,
        }
