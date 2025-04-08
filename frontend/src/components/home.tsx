import React, { useState } from "react";
import { Avatar } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import ChatContainer from "./chat/ChatContainer";
import ProfileDropdown from "./auth/ProfileDropdown";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";

interface HomeProps {
  isAuthenticated: boolean;
}

const Home = ({ isAuthenticated }: HomeProps) => {

  const [aiEnabled, setAiEnabled] = useState(false); // true = AI On
  const [isHybrid, setIsHybrid] = useState(false); // false = Semantic, true = Hybrid
  const [isReranking, setIsreranking] = useState(false); // false = Semantic, true = Hybrid


  // Logic wrappers
  const handleAiEnabledChange = (checked) => {
    if (checked) {
      setIsHybrid(true); // force Hybrid ON
      setAiEnabled(true); // allow AI
    } else {
      setAiEnabled(false); // just turn AI off
    }
  };

  const handleIsHybridChange = (checked) => {
    setIsHybrid(checked);
    if (!checked) {
      setAiEnabled(false); // turn AI off if Hybrid is disabled
    }
  };


  return (
    <div className="flex flex-col h-screen w-full bg-background">
      {/* Header */}
      <header className="h-16 border-b flex items-center justify-between px-4 md:px-6 bg-background">
        <div className="flex items-center space-x-3">
          <div className="h-8 w-8 rounded-full overflow-hidden">
            <img
              src="/logo256.png"
              alt="App Logo"
              className="h-full w-full object-contain"
            />
          </div>
          <h1 className="text-xl font-semibold leading-tight">
            Lightweight Movie search
            <div className="text-sm text-muted-foreground leading-none">
              by Christian Leiva Beltran · v0.01
            </div>
          </h1>
        </div>
  
        {/* Toggles + Profile */}
        <div className="flex items-center">
          {/* Toggle Group */}
          <div className="flex items-center space-x-4 mr-2">
            {/* AI Toggle */}
            <div className="flex items-center space-x-2">
              <Label htmlFor="ai-toggle" className="text-sm">LLM</Label>
              <Switch
                id="ai-toggle"
                checked={aiEnabled}
                onCheckedChange={handleAiEnabledChange}
              />
            </div>
  
            {/* Retrieval Toggle */}
            <div className="flex items-center space-x-2">
              <Label htmlFor="retrieval-toggle" className="text-sm">Hybrid Search</Label>
              <Switch
                id="retrieval-toggle"
                checked={isHybrid}
                onCheckedChange={handleIsHybridChange}
              />
            </div>
          </div>
  
          {/* ProfileDropdown with slight left shift (via margin) */}
          <div className="mr-5">
          <ProfileDropdown
              isLoggedIn={isAuthenticated}
              userName={isAuthenticated ? "Christian Leiva" : "CL"}
              userEmail={"chris@chrisgenai.com"}
              onLogin={() => {}}
              onLogout={() => {}}
            />
          </div>
        </div>
      </header>
  
      {/* Main Content */}
      <main className="flex-1 overflow-hidden">
        <ChatContainer
          aiEnabled={aiEnabled}
          isHybrid={isHybrid}
          isReranking={isReranking}
        />
      </main>
    </div>
  );
  
};

export default Home;
