import React from 'react';

type Movie = {
  _id: string | { $oid: string } | null;
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
  imdb?: { rating?: number; votes?: number; id?: number };
  tomatoes?: {
    viewer?: { rating?: number; meter?: number };
    critic?: { rating?: number; numReviews?: number; meter?: number };
    boxOffice?: string;
    website?: string;
  };
  released?: string;
  num_mflix_comments?: number;
  score?: number;
  source_embedding?: string;
  vs_score?: number;
  fts_score?: number;
};

interface MovieCardProps {
  movie: Movie;
}

const truncate = (text: string = '', max = 1000) =>
  text.length > max ? text.slice(0, max) + '…' : text;

const MovieCard: React.FC<MovieCardProps> = ({ movie }) => {
  return (
    <div className="flex flex-col lg:flex-row bg-gray-800 rounded-2xl shadow-lg overflow-hidden p-4 h-full">
      <div className="flex flex-col md:flex-row bg-gray-800 rounded-2xl shadow-lg overflow-hidden mb-6 p-4">
      <img
          src={movie.poster?.trim() || '/fallback-poster.png'}
          alt={movie.title}
          onError={(e) => {
            e.currentTarget.onerror = null;
            e.currentTarget.src = '/fallback-poster.png';
          }}
          className="
            w-auto
            max-w-[220px]
            max-h-[320px]
            object-contain
            rounded-lg
            mb-4
            md:mb-0
            md:mr-6
            mx-auto
          "
        />
        <div className="flex flex-col text-white space-y-2">
          <h2 className="text-2xl font-bold">
            {movie.title} {movie.year && <span className="text-gray-400">({movie.year})</span>}
          </h2>

          <p className="text-sm text-gray-300">
            {truncate(movie.fullplot || movie.plot)}
          </p>

          <div className="flex flex-wrap text-sm gap-x-4 gap-y-1 mt-2">
            {movie.genres && <span>🎭 {movie.genres.join(', ')}</span>}
            {movie.runtime && <span>⏱ {movie.runtime} min</span>}
            {movie.rated && <span>🔞 Rated: {movie.rated}</span>}
          </div>

          {movie.directors && (
            <p>👨‍🎓 <strong>Director(s):</strong> {movie.directors.join(', ')}</p>
          )}
          {movie.cast && (
            <p>🎤 <strong>Cast:</strong> {movie.cast.slice(0, 5).join(', ')}</p>
          )}
          
          <div className="flex flex-wrap text-sm gap-x-4 gap-y-1 mt-2">

          {movie.languages && (
            <p>🗣 <strong>Languages:</strong> {movie.languages.join(', ')}</p>
          )}
          
          {movie.countries && (
            <p>🌍 <strong>Countries:</strong> {movie.countries.join(', ')}</p>
          )}

          </div>

          <div className="flex flex-wrap text-sm gap-x-4 gap-y-1 mt-2">
          {movie.imdb && (
            <p>
              ⭐ <strong>IMDb:</strong> {movie.imdb.rating ?? 'N/A'} ({movie.imdb.votes ?? 0} votes)
            </p>
          )}

          {movie.tomatoes?.viewer && (
            <p>🍅 <strong>Tomatoes (Viewers):</strong> {movie.tomatoes.viewer.rating}/5 ({movie.tomatoes.viewer.meter}%)</p>
          )}
          </div>

          {movie.tomatoes?.critic && (
            <p>🎬 <strong>Critics:</strong> {movie.tomatoes.critic.rating}/10 ({movie.tomatoes.critic.numReviews} reviews, {movie.tomatoes.critic.meter}%)</p>
          )}

          {movie.tomatoes?.boxOffice && (
            <p>💰 <strong>Box Office:</strong> {movie.tomatoes.boxOffice}</p>
          )}

          {movie.tomatoes?.website && (
            <p>🌐 <a href={movie.tomatoes.website} className="underline text-blue-400" target="_blank" rel="noopener noreferrer">Official Website</a></p>
          )}

          {movie.awards?.text && (
            <p>🏆 <strong>Awards:</strong> {movie.awards.text}</p>
          )}

          {/* Subtle Evaluation Metadata */}
            {/* Subtle Evaluation Metadata */}
            {(movie.score !== undefined || movie.source_embedding || movie._id) && (
              <div className="text-xs text-gray-500 mt-4 italic">
                {movie.score !== undefined && <>Score: {movie.score.toFixed(4)} </>}
                {movie.vs_score !== undefined && <>| VS_Score: {movie.vs_score.toFixed(4)} </>}
                {movie.fts_score !== undefined && <>| TS_Score: {movie.fts_score.toFixed(8)} </>}
                
                {movie._id && (
                  <>
                    | ID:{' '}
                    {typeof movie._id === 'string'
                      ? movie._id
                      : (movie._id as { $oid: string }).$oid}
                  </>
                )}
                {movie.source_embedding && <> | Source: {movie.source_embedding}</>}
              </div>
            )}
        </div>
      </div>
    </div>
  );
};

export default MovieCard;
