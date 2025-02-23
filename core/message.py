# Message分为几种：对话消息，请求消息，附件；
import asyncio
import json
import os.path
import uuid
import datetime
from abc import ABC
from asyncio import Queue, QueueEmpty, wait_for
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Type, TypeVar, Union, Set
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PrivateAttr,
    field_serializer,
    field_validator,
    model_serializer,
    model_validator,
)


class Attachment(BaseModel):
    content_type: str = Field(default="text")
    content: str


class Message(Attachment):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender: str
    receiver: Set[str]
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    attachments: Dict[str, Union[Attachment | "Message"]]

    def cat(self, *messages: "Message") -> "Message":
        combined_attachments = self.attachments.copy()
        combined_content = self.content
        for message in messages:
            combined_attachments.update(message.attachments)
            combined_content += message.content

        return Message(
            sender=self.sender,
            receiver=self.receiver,
            timestamp=datetime.datetime.now(),
            attachments=combined_attachments
        )
# MessageStack有以下功能：将多轮对话转变成chat_messages，将多人对话转变为历史对话记录，将流式输出储存。


class MessageStack(BaseModel):
    system_message: str = Field(default=None)
    messages: List[Message] = Field(default_factory=list)


class ChatHistoryStack(MessageStack):
    def to_chat_messages(self) -> List[Dict]:
        ret = []
        if self.system_message:
            ret.append({"role": "system", "content": self.system_message})
        for index, message in enumerate(self.messages):
            role = "user" if index % 2 == 0 else "assistant"
            ret.append({"role": role, "content": message.content})
        return ret
