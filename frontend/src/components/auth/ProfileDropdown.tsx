import React from "react";
import { LogIn, LogOut, User, Settings, HelpCircle } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";

interface ProfileDropdownProps {
  isLoggedIn?: boolean;
  userName?: string;
  userEmail?: string;
  userAvatarUrl?: string;
  onLogin?: () => void;
  onLogout?: () => void;
  onSettings?: () => void;
  onHelp?: () => void;
  onProfile?: () => void;
}


const onLogout = () => {
  localStorage.removeItem("id_token");
  localStorage.removeItem("refresh_token");

  const logoutUrl = `https://auth.mongoagent.com/logout?client_id=2fvd6tbv3a46rlu3shr14oj93b&logout_uri=${encodeURIComponent("https://mongoagent.com")}`;

  window.location.href = logoutUrl;
};



const ProfileDropdown = ({
  isLoggedIn = false,
  userName = "Guest User",
  userEmail = "guest@example.com",
  userAvatarUrl = "",
  onLogin = () => console.log("Login clicked"),
  onLogout = () => {},
  onSettings = () => console.log("Settings clicked"),
  onHelp = () => console.log("Help clicked"),
  onProfile = () => console.log("Profile clicked"),
}: ProfileDropdownProps) => {
  // Get initials for avatar fallback
  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase();
  };


  const handleLogout = () => {
    localStorage.removeItem("id_token");
    localStorage.removeItem("refresh_token");
    const logoutUrl = `https://auth.mongoagent.com/logout?client_id=2fvd6tbv3a46rlu3shr14oj93b&logout_uri=${encodeURIComponent("https://mongoagent.com")}`;
    window.location.href = logoutUrl;

    if (onLogout) {
      onLogout();
    }
  };


  return (
    <div className="bg-background">
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" className="relative h-10 w-10 rounded-full">
            <Avatar>
              {userAvatarUrl ? (
                <AvatarImage src={userAvatarUrl} alt={userName} />
              ) : (
                <AvatarFallback>{getInitials(userName)}</AvatarFallback>
              )}
            </Avatar>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent className="w-56" align="end">
          {isLoggedIn ? (
            <>
              <DropdownMenuLabel>
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium">{userName}</p>
                  <p className="text-xs text-muted-foreground">{userEmail}</p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={onProfile}>
                <User className="mr-2 h-4 w-4" />
                <span>Profile</span>
              </DropdownMenuItem>
              <DropdownMenuItem onClick={onSettings}>
                <Settings className="mr-2 h-4 w-4" />
                <span>Settings</span>
              </DropdownMenuItem>
              <DropdownMenuItem onClick={onHelp}>
                <HelpCircle className="mr-2 h-4 w-4" />
                <span>Help</span>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleLogout}>
                <LogOut className="mr-2 h-4 w-4" />
                <span>Log out</span>
              </DropdownMenuItem>
            </>
          ) : (
            <>
              <DropdownMenuLabel>Account</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleLogout}>
              <LogOut className="mr-2 h-4 w-4" />
                <span>Log out</span>
              </DropdownMenuItem>
              <DropdownMenuItem onClick={onHelp}>
                <HelpCircle className="mr-2 h-4 w-4" />
                <span>Help</span>
              </DropdownMenuItem>
            </>
          )}
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
};

export default ProfileDropdown;
