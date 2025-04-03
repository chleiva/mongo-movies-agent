// components/sidebar/DocumentSidebar.tsx
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface DocumentSidebarProps {
  url?: string;
  isOpen: boolean;
  onToggle: () => void;
}

const DocumentSidebar = ({ url, isOpen, onToggle }: DocumentSidebarProps) => {
  return (
    <div
      className={cn(
        "fixed top-0 right-0 h-full z-50 flex flex-col border-l bg-background transition-all duration-300 ease-in-out shadow-lg",
        isOpen ? "w-[800px]" : "w-[40px]"
      )}
    >
      <div className="flex items-center justify-between p-4">
        {isOpen && (
          <h2 className="text-sm font-medium truncate max-w-[500px]">
            {url}
          </h2>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggle}
          className="ml-auto"
        >
          {isOpen ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </Button>
      </div>
      {isOpen && url && (
        <iframe
          key={url}
          src={url}
          className="flex-1 border-none w-full"
          title="Document Preview"
        />
      )}
    </div>
  );
};

export default DocumentSidebar;
