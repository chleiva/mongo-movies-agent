import React from 'react';
import MovieCard from './MovieCard';

export interface Movie {
  _id: string;
  title: string;
  year?: number;
  plot?: string;
  fullplot?: string;
  genres?: string[];
  runtime?: number;
  cast?: string[];
  poster?: string;
  directors?: string[];
  languages?: string[];
  countries?: string[];
  rated?: string;
  awards?: { text?: string };
  imdb?: { rating?: number; votes?: number };
  tomatoes?: {
    viewer?: { rating?: number; meter?: number };
    critic?: { rating?: number; meter?: number };
  };
}

interface MovieListProps {
  movies: Movie[];
  loading?: boolean;
}

const MovieList: React.FC<MovieListProps> = ({ movies, loading = false }) => {
  if (loading) {
    return (
        <div className="p-4 flex flex-col gap-4">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="bg-gray-800 p-4 rounded-2xl animate-pulse h-72" />
        ))}
      </div>
    );
  }

  return (
    <div className="p-4 flex flex-col gap-4">
        {movies.map((movie) => {
        let id: string;

        const rawId = movie._id;

        if (
            rawId !== null &&
            typeof rawId === 'object' &&
            rawId !== undefined &&
            Object.prototype.hasOwnProperty.call(rawId, '$oid')
        ) {
            id = (rawId as { $oid: string }).$oid;
        } else if (typeof rawId === 'string') {
            id = rawId;
        } else {
            id = crypto.randomUUID(); // fallback
        }

        return <MovieCard key={id} movie={{ ...movie, _id: id }} />;
        })}
    </div>
  );
};

export default MovieList;
