import React, { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Paperclip, Send, X } from "lucide-react";

interface MessageInputProps {
  onSendMessage?: (message: string) => void;
  onAttachFile?: (file: File) => void;
  isLoading?: boolean;
}

const MessageInput = ({
  onSendMessage = () => {},
  onAttachFile = () => {},
  isLoading = false,
}: MessageInputProps) => {
  const [message, setMessage] = useState("");
  const [attachedFile, setAttachedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSendMessage = () => {
    if (message.trim() || attachedFile) {
      onSendMessage(message);
      setMessage("");
      // Keep the file attached after sending the message
      // The file will be cleared when the user explicitly removes it
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      // Check if file is a PDF
      if (file.type === "application/pdf") {
        setAttachedFile(file);
        onAttachFile(file);
      } else {
        // Show error or notification that only PDFs are allowed
        alert("Only PDF files are allowed");
      }
    }
  };

  const handleAttachClick = () => {
    fileInputRef.current?.click();
  };

  const handleRemoveFile = () => {
    setAttachedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="bg-background border-t p-4 flex flex-col gap-2 w-full">
      {/* Attached file preview */}
      {attachedFile && (
        <div className="flex items-center gap-2 p-2 bg-muted rounded-md">
          <Paperclip className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm truncate flex-1">{attachedFile.name}</span>
          <Button
            variant="ghost"
            size="sm"
            className="h-6 w-6 p-0"
            onClick={handleRemoveFile}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      )}

      {/* Input area */}
      <div className="flex items-center gap-2">
        <Input
          type="text"
          placeholder="Type your message..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          className="flex-1 rounded-full text-lg"
          disabled={isLoading}
        />


        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                size="icon"
                className="rounded-full"
                onClick={handleSendMessage}
                disabled={isLoading || (!message.trim() && !attachedFile)}
              >
                <Send className="h-5 w-5" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              <p>Send message</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>

        {/* Hidden file input */}
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept="application/pdf"
          className="hidden"
        />
      </div>
    </div>
  );
};

export default MessageInput;
