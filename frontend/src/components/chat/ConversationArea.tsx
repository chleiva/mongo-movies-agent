import React, { useRef, useEffect } from "react";
import { Avatar } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { FileText, Clock } from "lucide-react";
import ReactMarkdown from "react-markdown";

interface Message {
  id: string;
  content: string;
  sender: "user" | "bot";
  timestamp: Date;
  documentReferences?: DocumentReference[];
  isLoading?: boolean;
}

interface DocumentReference {
  id: string;
  name: string;
  url: string;
}

interface ConversationAreaProps {
  messages?: Message[];
  onDocumentClick?: (document: DocumentReference) => void;
  onUrlClick?: (url: string) => void;
}

const ConversationArea = ({
  messages = [
    {
      id: "1",
      content: "Hello! I'm your AI assistant for manufacturing documents. How can I help you today?",
      sender: "bot",
      timestamp: new Date(Date.now() - 60000 * 5),
    },
  ],
  onDocumentClick = () => {},
  onUrlClick = () => {}, 
}: ConversationAreaProps) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  return (
    <div className="flex flex-col h-full w-full bg-gray-50 dark:bg-gray-900">
      <ScrollArea className="flex-1 p-4">
        <div className="flex flex-col space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`flex ${message.sender === "user" ? "flex-row-reverse" : "flex-row"} items-start gap-2 max-w-[80%]`}
              >
                <Avatar className="h-8 w-8 mt-1">
                  {message.sender === "user" ? (
                    <div className="h-full w-full rounded-full bg-blue-500 flex items-center justify-center text-white font-medium">
                      U
                    </div>
                  ) : (
                    <div className="h-full w-full rounded-full bg-purple-500 flex items-center justify-center text-white font-medium">
                      S
                    </div>
                  )}
                </Avatar>

                <div className="flex flex-col">
                  <div
                    className={`rounded-2xl px-4 py-2 ${
                      message.sender === "user"
                        ? "bg-blue-500 text-white"
                        : "bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700"
                    }`}
                  >
                        {message.isLoading ? (
                          <div className="flex items-center space-x-1">
                            <div
                              className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce"
                              style={{ animationDelay: "0ms" }}
                            ></div>
                            <div
                              className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce"
                              style={{ animationDelay: "150ms" }}
                            ></div>
                            <div
                              className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce"
                              style={{ animationDelay: "300ms" }}
                            ></div>
                          </div>
                        ) : (
                          <div className="prose prose-base md:prose-lg dark:prose-invert max-w-none">
                          <ReactMarkdown
                            components={{
                              a: ({ node, ...props }) => (
                                <a
                                  {...props}
                                  onClick={(e) => {
                                    e.preventDefault();
                                    if (props.href) onUrlClick(props.href);
                                  }}
                                  className="text-blue-400 underline hover:text-blue-300 transition cursor-pointer"
                                />
                              ),
                            }}
                          >
                            {message.content}
                          </ReactMarkdown>
                          </div>
                        )}


                    {message.documentReferences &&
                      message.documentReferences.length > 0 && (
                        <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                          <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">
                            Referenced documents:
                          </p>
                          <div className="flex flex-wrap gap-2">
                            {message.documentReferences.map((doc) => (
                              <TooltipProvider key={doc.id}>
                                <Tooltip>
                                  <TooltipTrigger asChild>
                                    <button
                                      onClick={() => onDocumentClick(doc)}
                                      className="flex items-center gap-1 px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded-lg text-sm hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                                    >
                                      <FileText className="h-3.5 w-3.5" />
                                      <span className="truncate max-w-[150px]">
                                        {doc.name}
                                      </span>
                                    </button>
                                  </TooltipTrigger>
                                  <TooltipContent>
                                    <p>Click to view document</p>
                                  </TooltipContent>
                                </Tooltip>
                              </TooltipProvider>
                            ))}
                          </div>
                        </div>
                      )}
                  </div>

                  <div
                    className={`flex items-center mt-1 text-xs text-gray-500 ${message.sender === "user" ? "justify-end" : "justify-start"}`}
                  >
                    <Clock className="h-3 w-3 mr-1" />
                    <span>{formatTime(message.timestamp)}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>
    </div>
  );
};

export default ConversationArea;
