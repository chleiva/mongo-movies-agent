import { useEffect, useState } from "react";
import { Suspense } from "react";
import { Routes, Route, useLocation } from "react-router-dom";
import Home from "./components/home";
import PrivacyPolicy from "./components/PrivacyPolicy"; // Add PrivacyPolicy component
import TermsOfService from "./components/TermsOfService"; // Add TermsOfService component
import routes from "tempo-routes";


const COGNITO_DOMAIN = "https://auth.mongoagent.com";
const CLIENT_ID = "2fvd6tbv3a46rlu3shr14oj93b";
const REDIRECT_URI = window.location.origin; // auto resolves to http://localhost:5173 or https://mongoagent.com
const RESPONSE_TYPE = "code";
const SCOPE = "openid email profile";

function App() {
  const [authLoading, setAuthLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const location = useLocation();


  function RedirectToCognito() {
    useEffect(() => {
      const loginUrl = `${COGNITO_DOMAIN}/oauth2/authorize?response_type=${RESPONSE_TYPE}&client_id=${CLIENT_ID}&redirect_uri=${encodeURIComponent(
        REDIRECT_URI
      )}&scope=${encodeURIComponent(SCOPE)}`;
      window.location.href = loginUrl;
    }, []);
  
    return (
      <div className="flex flex-col items-center justify-center h-screen text-center space-y-4">
        <p>Redirecting to login...</p>
      </div>
    );
  }
  

  useEffect(() => {
    const savedTheme = localStorage.getItem("theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const isDark = savedTheme === "dark" || (!savedTheme && prefersDark);
    document.documentElement.classList.toggle("dark", isDark);
  }, []);

  useEffect(() => {
    const isTokenExpired = (token) => {
      try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        return payload.exp * 1000 < Date.now();
      } catch (e) {
        return true;
      }
    };

    const refreshAccessToken = async (refreshToken) => {
      const body = new URLSearchParams({
        grant_type: "refresh_token",
        client_id: CLIENT_ID,
        refresh_token: refreshToken,
      });

      const response = await fetch(`${COGNITO_DOMAIN}/oauth2/token`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: body,
      });

      const tokens = await response.json();

      if (tokens.id_token) {
        localStorage.setItem("id_token", tokens.id_token);
        if (tokens.refresh_token) {
          localStorage.setItem("refresh_token", tokens.refresh_token);
        }
        return true;
      }
      return false;
    };


    const initAuth = async () => {
      setAuthLoading(true);
    
      const params = new URLSearchParams(location.search);
      const code = params.get("code");
    
      const idToken = localStorage.getItem("id_token");
      const refreshToken = localStorage.getItem("refresh_token");
    
      if (idToken && !isTokenExpired(idToken)) {
        setIsAuthenticated(true);
        setAuthLoading(false); // ✅ FIXED
        return;
      }
    
      if (refreshToken) {
        const success = await refreshAccessToken(refreshToken);
        if (success) {
          setIsAuthenticated(true);
          setAuthLoading(false); // ✅ FIXED
          return;
        } else {
          localStorage.removeItem("id_token");
          localStorage.removeItem("refresh_token");
        }
      }
    
      // Exchange the code
      if (code) {
        try {
          const body = new URLSearchParams({
            grant_type: "authorization_code",
            client_id: CLIENT_ID,
            code,
            redirect_uri: REDIRECT_URI,
          });
    
          const response = await fetch(`${COGNITO_DOMAIN}/oauth2/token`, {
            method: "POST",
            headers: {
              "Content-Type": "application/x-www-form-urlencoded",
            },
            body,
          });
    
          const tokens = await response.json();
    
          if (tokens.id_token) {
            localStorage.setItem("id_token", tokens.id_token);
            if (tokens.refresh_token) {
              localStorage.setItem("refresh_token", tokens.refresh_token);
            }
    
            window.history.replaceState({}, document.title, "/");
    
            setIsAuthenticated(true);
            setAuthLoading(false); // ✅ FIXED
            return;
          }
        } catch (error) {
          console.error("❌ Token exchange failed", error);
        }
    
        window.history.replaceState({}, document.title, "/");
      }
    
      setAuthLoading(false); // ✅ Final fallback
    };
    
      

    initAuth();
  }, [location]);

  const login = () => {
    const loginUrl = `${COGNITO_DOMAIN}/oauth2/authorize?response_type=${RESPONSE_TYPE}&client_id=${CLIENT_ID}&redirect_uri=${encodeURIComponent(
      REDIRECT_URI
    )}&scope=${encodeURIComponent(SCOPE)}`;
    window.location.href = loginUrl;
  };

  return (
    <div className="flex flex-col min-h-screen">
      <Suspense fallback={<p>Loading...</p>}>
        <main className="flex-grow">
          {authLoading ? (
            <div className="flex items-center justify-center h-full">
              <p>Checking login...</p>
            </div>
          ) : (
            <Routes>
              {/* Public routes */}
              <Route path="/privacy-policy" element={<PrivacyPolicy />} />
              <Route path="/terms-of-service" element={<TermsOfService />} />
  
              {/* Protected routes */}
              {isAuthenticated ? (
                <>
                  <Route path="/" element={<Home isAuthenticated={isAuthenticated} />} />
                  {import.meta.env.VITE_TEMPO === "true" && routes}
                </>
              ) : (
                <Route path="*" element={<RedirectToCognito />} />
              )}
            </Routes>
          )}
        </main>
      </Suspense>
    </div>
  );  
}

export default App;
