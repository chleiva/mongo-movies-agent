import React, { useState, useEffect } from "react";
import ConversationArea from "./ConversationArea";
import MessageInput from "./MessageInput";
import DocumentSidebar from "../sidebar/DocumentSidebar";

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

interface AppDocument extends DocumentReference {
  isReferenced?: boolean;
}

interface ChatContainerProps {
  initialMessages?: Message[];
  initialDocuments?: AppDocument[];
}

const ChatContainer = ({
  initialMessages = [
    {
      id: "1",
      content: "Hello! I'm your AI assistant for manufacturing documents  .... You can ask me things like: Provide Safety information for FANUC robots or Installation instructions for Ligent Robot inCube20 ..... How can I help you today?",
      sender: "bot",
      timestamp: new Date(Date.now() - 60000 * 5),
    },
  ],
  initialDocuments = [],
}: ChatContainerProps) => {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [documents, setDocuments] = useState<AppDocument[]>(
    initialDocuments ?? []
  );  
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarUrl, setSidebarUrl] = useState<string | null>(null);


  // Show sidebar if there are any referenced documents
  useEffect(() => {
    const hasReferencedDocs = documents.some((doc) => doc.isReferenced);
    if (hasReferencedDocs && !isSidebarOpen) {
      setIsSidebarOpen(true);
    }
  }, [documents, isSidebarOpen]);

  function isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Math.floor(Date.now() / 1000);
      return payload.exp < currentTime;
    } catch (e) {
      return true; // If decoding fails, treat it as expired
    }
  }
  
  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return;
  
    const idToken = localStorage.getItem("id_token");
    // Only require idToken
    if (!idToken || isTokenExpired(idToken)) {
      // Redirect to homepage if not logged in
      window.location.href = "/";
      return;
    }
    
    // Optionally get userId if it exists
    const userId = localStorage.getItem("user_id");
    
  
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      sender: "user",
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
  
    // Show loading bubble
    const loadingMessage: Message = {
      id: `loading-${Date.now()}`,
      content: "",
      sender: "bot",
      timestamp: new Date(),
      isLoading: true,
    };
    setMessages((prev) => [...prev, loadingMessage]);
    setIsLoading(true);
  
    try {
      const response = await fetch(
        "https://o43zaz9tv7.execute-api.us-west-2.amazonaws.com/prod/user/message",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${idToken}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_id: "userId",
            request: content,
            history: messages.map((msg) => ({
              sender: msg.sender,
              content: msg.content,
              timestamp: msg.timestamp,
            })),
          }),
        }
      );
    
      console.log("HTTP Status:", response.status, response.statusText);
    
      const text = await response.text();
      console.log("Raw Response Body:", text);
    
      let responseJson;
      try {
        responseJson = JSON.parse(text);
      } catch (e) {
        console.error("Failed to parse JSON:", e);
        responseJson = {};
      }
    
      const botResponse =
        responseJson.response !== undefined && responseJson.response !== null
          ? responseJson.response
          : "No response from bot";
    
      console.log("Parsed bot response:", botResponse);
    
      setMessages((prev) =>
        prev
          .filter((msg) => !msg.isLoading)
          .concat({
            id: `bot-${Date.now()}`,
            content: botResponse,
            sender: "bot",
            timestamp: new Date(),
          })
      );
    } catch (err) {
      console.error("Error calling API:", err);
      setMessages((prev) =>
        prev
          .filter((msg) => !msg.isLoading)
          .concat({
            id: `bot-${Date.now()}`,
            content: "Apologies, error trying to contact the AI agent API.",
            sender: "bot",
            timestamp: new Date(),
          })
      );
    } finally {
      setIsLoading(false);
    }
    
  };
  



  const handleAttachFile = (file: File) => {
    // Create a new document from the file
    const newDocument: AppDocument = {
      id: `doc-${Date.now()}`,
      name: file.name,
      url: URL.createObjectURL(file),
      isReferenced: false,
    };

    setDocuments((prev) => [...prev, newDocument]);

    // Add a system message about the uploaded document
    const systemMessage: Message = {
      id: `system-${Date.now()}`,
      content: `You've uploaded "${file.name}". I'll analyze this document for you.`,
      sender: "bot",
      timestamp: new Date(),
      documentReferences: [newDocument],
    };

    setMessages((prev) => [...prev, systemMessage]);

    // Mark the document as referenced
    setDocuments((prev) =>
      prev.map((doc) => {
        if (doc.id === newDocument.id) {
          return { ...doc, isReferenced: true };
        }
        return doc;
      }),
    );
  };

  const handleDocumentClick = (document: DocumentReference) => {
    // Highlight the document in the sidebar
    setDocuments((prev) =>
      prev.map((doc) => {
        if (doc.id === document.id) {
          return { ...doc, isReferenced: true };
        }
        return doc;
      }),
    );

    // Ensure sidebar is open
    setIsSidebarOpen(true);
  };

  const handleViewDocument = (doc: AppDocument) => {
    window.open(doc.url, "_blank");
  };

  const handleDownloadDocument = (doc: AppDocument) => {
    const link = document.createElement("a");
    link.href = doc.url;
    link.download = doc.name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
   };
  

  const toggleSidebar = () => {
    setIsSidebarOpen((prev) => !prev);
  };

  return (
    <div className="flex h-full w-full bg-background">
      {/* Document Sidebar */}
      <DocumentSidebar
        url={sidebarUrl ?? undefined}
        isOpen={isSidebarOpen}
        onToggle={toggleSidebar}
      />


      {/* Chat Area */}
      <div
        className={`flex flex-col h-full overflow-hidden transition-all duration-300 ${
          isSidebarOpen ? "w-[calc(100%-800px)]" : "w-[calc(100%-40px)]"
        } min-w-[300px]`}
      >
        {/* Conversation Area */}
        <ConversationArea
          messages={messages}
          onDocumentClick={handleDocumentClick}
          onUrlClick={(url) => {
            setSidebarUrl(url);
            setIsSidebarOpen(true);
          }}
        />


        {/* Message Input */}
        <MessageInput
          onSendMessage={handleSendMessage}
          onAttachFile={handleAttachFile}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
};

export default ChatContainer;
