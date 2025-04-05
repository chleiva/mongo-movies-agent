import React, { useState } from "react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { MessageSquare, User, LogOut, LogIn, UserPlus } from "lucide-react";
// Removed the unused import for ProfileDropdown

interface HeaderProps {
  isLoggedIn?: boolean;
  userName?: string;
  userAvatar?: string;
  onLogin?: () => void;
  onSignup?: () => void;
  onLogout?: () => void;
}



const Header = ({
  isLoggedIn = false,
  userName = "Guest User",
  userAvatar = "",
  onLogin = () => {},
  onSignup = () => {},
  onLogout = () => {},
}: HeaderProps) => {
  const [isProfileOpen, setIsProfileOpen] = useState(false);

  return (


    <header className="w-[calc(100%-40px) h-16 bg-background border-b border-border flex items-center justify-between px-4 md:px-6 sticky top-0 z-50">


<div className="flex items-center gap-2 bg-black p-2">
  <div className="w-8 h-8 rounded-full overflow-hidden border border-red-500 bg-white">
  <img
  src="https://via.placeholder.com/32"
  alt="Test"
  className="w-8 h-8 rounded-full object-contain"
/>

  </div>
  <h1 className="text-xl font-semibold hidden sm:block">
    MongoDB Manufacturing AI Assistant
  </h1>
</div>

      <div className="flex items-center gap-2">
        {isLoggedIn ? (
          <DropdownMenu open={isProfileOpen} onOpenChange={setIsProfileOpen}>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                className="relative h-10 w-10 rounded-full"
              >
                <Avatar className="h-10 w-10">
                  <AvatarImage src={userAvatar} alt={userName} />
                  <AvatarFallback className="bg-primary/10">
                    {userName.slice(0, 2).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <div className="flex items-center justify-start gap-2 p-2">
                <div className="flex flex-col space-y-1 leading-none">
                  <p className="font-medium">{userName}</p>
                </div>
              </div>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <User className="mr-2 h-4 w-4" />
                <span>Profile</span>
              </DropdownMenuItem>
              <DropdownMenuItem onClick={onLogout}>
                <LogOut className="mr-2 h-4 w-4" />
                <span>Log out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ) : (
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={onLogin}>
              <LogIn className="mr-2 h-4 w-4" />
              <span className="hidden sm:inline">Login</span>
            </Button>
            <Button variant="default" size="sm" onClick={onSignup}>
              <UserPlus className="mr-2 h-4 w-4" />
              <span className="hidden sm:inline">Sign up</span>
            </Button>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
