import React, { useState, useEffect } from "react";
import ConversationArea from "./ConversationArea";
import MessageInput from "./MessageInput";
import MovieSidebar from "../sidebar/MovieSidebar";
import MovieList, { Movie } from '../MovieList';


const COGNITO_DOMAIN = "https://auth.mongoagent.com";
const CLIENT_ID = "2fvd6tbv3a46rlu3shr14oj93b";
const REDIRECT_URI = window.location.origin; // auto resolves to http://localhost:5173 or https://mongoagent.com
const RESPONSE_TYPE = "code";
const SCOPE = "openid email profile";
const apiBaseUrl = "https://hgbb1jpvec.execute-api.us-west-2.amazonaws.com/prod/"


interface Message {
  id: string;
  content: string;
  sender: "user" | "bot";
  timestamp: Date;
  documentReferences?: DocumentReference[];
  isLoading?: boolean;
}

interface ChatContainerProps {
  initialMessages?: Message[];
  initialDocuments?: AppDocument[];
  aiEnabled: boolean;
  isHybrid: boolean;
  isReranking: boolean;
}



interface ParsedCurl {
  method: string;
  path: string;
  body: any | null;
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
      content: "Hello, I am your movies expert, ask me any question about a movie in natural language, or type a curl command to call my API.",
      sender: "bot",
      timestamp: new Date(Date.now() - 60000 * 5),
    },
  ],
  initialDocuments = [],
  aiEnabled,
  isHybrid,
  isReranking,
}: ChatContainerProps) => {

  const [movieResults, setMovieResults] = useState<Movie[]>([]);
  const [lastQuery, setLastQuery] = useState<string>("");
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [documents, setDocuments] = useState<AppDocument[]>(
    initialDocuments ?? []
  );  
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarUrl, setSidebarUrl] = useState<string | null>(null);

  
  const parseCurlCommand = (curl: string): ParsedCurl | null => {
    try {
      const methodMatch = curl.match(/-X\s+(GET|POST|PUT|DELETE|PATCH)/i);
      const dataMatch = curl.match(/--data|-d\s+'([^']+)'/);
      
      // NEW: match either full URL or relative path
      const urlMatch = curl.match(/curl\s+(-X\s+\w+\s+)?(['"]?)([^'" ]+)\2/);
      const rawPath = urlMatch ? urlMatch[3] : null;
  
      if (!rawPath) return null;
  
      const method = methodMatch ? methodMatch[1].toUpperCase() : "GET";
      const path = rawPath.startsWith("/") ? rawPath : `/${rawPath}`;
      const body = dataMatch ? JSON.parse(dataMatch[1]) : null;
  
      return { method, path, body };
    } catch (e) {
      console.error("❌ Failed to parse curl:", e);
      return null;
    }
  };
  


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
    if (!idToken || isTokenExpired(idToken)) {
      alert("Your session expired. Redirecting to login.");
      window.location.href = `${COGNITO_DOMAIN}/oauth2/authorize?response_type=code&client_id=${CLIENT_ID}&redirect_uri=${encodeURIComponent(REDIRECT_URI)}&scope=${encodeURIComponent(SCOPE)}`;
      return;
    }
  
    const userId = localStorage.getItem("user_id");
  
    // Create a new user message.
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      content,
      sender: "user",
      timestamp: new Date(),
    };
  
    // Create a loading spinner message with a unique id.
    const loadingMessageId = `loading-${Date.now()}`;

    const loadingMessage: Message = {
      id: loadingMessageId,
      content: "",
      sender: "bot",
      timestamp: new Date(),
      isLoading: true,
    };
  
    // Append both messages using the functional update so we always start from the latest state.
    setMessages((prev) => [...prev, userMessage, loadingMessage]);
    setIsLoading(true);

    let botResponse;
    let movieList;

  
    try {
      if (content.trim().toLowerCase().startsWith("curl ")) {

        const parsed = parseCurlCommand(content.trim());

        console.log("parsed", parsed);
  
        if (!parsed) {
          return "❌ Sorry, I couldn't parse your curl command. Please check the format.";
        }
      
        try {
          const response = await fetch(`${apiBaseUrl}${parsed.path}`, {
            method: parsed.method,
            headers: {
              Authorization: `Bearer ${idToken}`,
              "Content-Type": "application/json",
            },
            body: parsed.body ? JSON.stringify(parsed.body) : undefined,
          });
      
          const status = response.status;
          const statusText = response.statusText;
      
          let responseBody: string;
          const contentType = response.headers.get("Content-Type") || "";
      
          if (contentType.includes("application/json")) {
            try {
              // Prevent trying to parse empty body (e.g., from DELETE 204 No Content)
              const text = await response.text();
              responseBody = text;
          
              if (text) {
                const json = JSON.parse(text);
                responseBody = JSON.stringify(json, null, 2);
              } else {
                responseBody = "{}"; // or a more descriptive fallback like 'No content'
              }
            } catch (err) {
              console.error("❌ JSON parsing failed:", err);
              responseBody = "Invalid JSON response";
            }
          } else {
            responseBody = await response.text();
          }
          
          console.log("ResponseBody >>>", responseBody);
          
          const formattedJson = [
            `📡 **API Response**`,
            `Status: \`${status} ${statusText}\``,
            responseBody || "*No content returned*"
          ].join("\n");
          
          botResponse = formattedJson;
          
        
        botResponse = formattedJson;
        
        

        } catch (error: any) {
          console.error("❌ Curl execution error:", error);
          botResponse = "There was an error processing the curl command or its response."
        }


      } else {
  

      const url = `${apiBaseUrl}movies/search` +
      `?hybrid=${isHybrid}` +
      `&agent=${aiEnabled}` +
      `&reranking=${isReranking}`;


      // Normal flow: call your movies API.
      const response = await fetch(
        url,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${idToken}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_id: userId,
            request: content,
            // IMPORTANT: Do not use the stale "messages" variable here.
            // If you need the full history, consider using a ref or maintain history in another state.
            // Here, we send just the new user message as history.
            history: [
              {
                sender: userMessage.sender,
                content: userMessage.content,
                timestamp: userMessage.timestamp,
              },
            ],
          }),
        }
      );
  
      const text = await response.text();
      let responseJson;
      try {
        responseJson = JSON.parse(text);
      } catch (e) {
        responseJson = {};
      }
  
      botResponse = responseJson.message || "Here are some movie results:";
      movieList = Array.isArray(responseJson.movies) ? responseJson.movies : [];
  
      setMovieResults(movieList);
      setIsSidebarOpen(true);
    }



      setLastQuery(content);

  
      // Remove the loading message and append the bot's response.
      setMessages((prev) =>
        prev
          .filter((msg) => msg.id !== loadingMessageId)
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
          .filter((msg) => msg.id !== loadingMessageId)
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



  const toggleSidebar = () => {
    setIsSidebarOpen((prev) => !prev);
  };

  return (
    <div className="flex h-full w-full bg-background">

      {/* Chat Area */}
      <div
        className={`flex flex-col h-full overflow-hidden transition-all duration-300 ${
          isSidebarOpen ? "w-[calc(100%-1100px)]" : "w-[calc(100%-40px)]"
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


      {/* Document Sidebar */}
      <MovieSidebar
        isOpen={isSidebarOpen}
        onToggle={toggleSidebar}
        movies={movieResults}
        query={lastQuery}
      />


      </div>
    </div>
  );
};

export default ChatContainer;
