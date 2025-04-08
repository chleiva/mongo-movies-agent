import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import MovieList from "../MovieList"; // import your MovieList
import { Movie } from "../MovieList"; // import the Movie type

interface MovieSidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  movies: Movie[];
  query?: string;
}

const MovieSidebar = ({ isOpen, onToggle, movies, query }: MovieSidebarProps) => {
  return (
        <div
          className={cn(
            "fixed top-16 right-0 h-[calc(100vh-4rem)] z-50 flex flex-col border-l bg-background transition-all duration-300 ease-in-out shadow-lg",
            isOpen
              ? "w-full sm:w-[90vw] md:w-[700px] lg:w-[1100px]"
              : "w-[40px]"
          )}
        >

      <div className="flex items-center justify-between p-4">
        {isOpen && (
          <h2 className="text-sm font-medium max-w-[500px] break-words leading-snug">
            {query ? `Results for: "${query}"` : "Movie Results"}
          </h2>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggle}
          className="ml-auto"
        >
          {isOpen ? <ChevronRight size={32} /> : <ChevronLeft size={32} />}
        </Button>
      </div>

      {isOpen && (
        <div className="flex-1 overflow-y-auto px-2 sm:px-4 pb-4">
        <MovieList movies={movies} />
        </div>
      )}
    </div>
  );
};

export default MovieSidebar;
