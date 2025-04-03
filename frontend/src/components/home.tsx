import React, { useState } from "react";
import { Avatar } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import ChatContainer from "./chat/ChatContainer";
import ProfileDropdown from "./auth/ProfileDropdown";

const Home = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
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
            AI Manufacturing Assistant
            <div className="text-sm text-muted-foreground leading-none">
              by Christian Leiva Beltran · v0.01
            </div>
          </h1>
        </div>

        <div className="flex items-center space-x-2">
          <ProfileDropdown
            isLoggedIn={isLoggedIn}
            userName={isLoggedIn ? "Christian Leiva" : "CL"}
            userEmail={
              isLoggedIn ? "chris@chrisgenai.com" : "chris@chrisgenai.com"
            }
            onLogin={handleLogin}
            onLogout={handleLogout}
          />
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 overflow-hidden">
        <ChatContainer />
      </main>
    </div>
  );
};

export default Home;
