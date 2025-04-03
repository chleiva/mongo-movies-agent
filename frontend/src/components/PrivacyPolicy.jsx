export default function PrivacyPolicy() {
    return (
      <div className="p-8 max-w-3xl mx-auto text-gray-800">
        <h1 className="text-3xl font-bold mb-4">Privacy Policy</h1>
        <p className="mb-4">
          Your privacy is important to us. This Privacy Policy outlines how we handle your information when you use our application.
        </p>
        
        <h2 className="text-xl font-semibold mb-2">Information Collection</h2>
        <p className="mb-4">
          We do not collect, store, or share any personal information. The application uses Google authentication solely for verifying your identity. No user data is retained on our servers.
        </p>
  
        <h2 className="text-xl font-semibold mb-2">Third-Party Services</h2>
        <p className="mb-4">
          Authentication is handled through Google (via AWS Cognito). We do not access or store your email, name, or profile information beyond what is required to confirm your login status during your session.
        </p>
  
        <h2 className="text-xl font-semibold mb-2">Data Sharing</h2>
        <p className="mb-4">
          We do not share any personal information with third parties. We do not use your data for advertising or analytics.
        </p>
  
        <h2 className="text-xl font-semibold mb-2">Cookies and Tracking</h2>
        <p className="mb-4">
          We do not use cookies or any tracking technologies.
        </p>
  
        <h2 className="text-xl font-semibold mb-2">Your Rights</h2>
        <p className="mb-4">
          Since we do not store any of your personal data, there is nothing to delete or manage. You are always free to stop using the app at any time.
        </p>
  
        <h2 className="text-xl font-semibold mb-2">Contact</h2>
        <p className="mb-4">
          If you have any questions about this Privacy Policy, please contact us at <a href="mailto:support@mongoagent.com" className="underline text-blue-600">support@mongoagent.com</a>.
        </p>
  
        <p className="text-sm text-gray-500 mt-8">Last updated: April 2, 2025</p>
      </div>
    );
  }
  