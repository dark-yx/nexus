"""YouTube tools."""
from __future__ import annotations
import json
from langchain_core.tools import BaseTool
from pydantic.v1 import BaseModel, Field
from typing import Type
from langchain_community.document_loaders import YoutubeLoader
from langchain_community.tools import YouTubeSearchTool

# --- Input Schemas ---
class LoadTranscriptInput(BaseModel):
    url: str = Field(description="The URL of the YouTube video.")

class SearchVideosInput(BaseModel):
    query: str = Field(description="The query to search for.")
    max_results: int = Field(description="The maximum number of results to return.", default=5)

# --- Tool Implementations ---

class YouTubeLangchainTool(BaseTool):
    """A base tool for interacting with YouTube."""
    name: str = "youtube_base_tool"
    description: str = "A base tool for YouTube operations."

    def _run(self, *args, **kwargs):
        raise NotImplementedError("This base tool should not be run directly.")

class LoadTranscriptTool(YouTubeLangchainTool):
    name: str = "load_youtube_transcript"
    description: str = "Loads the transcript of a YouTube video."
    args_schema: Type[BaseModel] = LoadTranscriptInput

    def _run(self, url: str) -> str:
        try:
            loader = YoutubeLoader.from_youtube_url(url, add_video_info=True)
            docs = loader.load()
            return docs[0].page_content
        except Exception as e:
            return f"An error occurred: {e}"

class SearchVideosTool(YouTubeLangchainTool):
    name: str = "search_youtube_videos"
    description: str = "Searches for YouTube videos based on a query."
    args_schema: Type[BaseModel] = SearchVideosInput

    def _run(self, query: str, max_results: int = 5) -> str:
        try:
            tool = YouTubeSearchTool()
            return tool.run(f"{query},{max_results}")
        except Exception as e:
            return f"An error occurred: {e}"