export default function TermsOfService() {
    return (
      <div className="p-8 max-w-3xl mx-auto text-gray-800">
        <h1 className="text-3xl font-bold mb-4">Terms of Service</h1>
  
        <p className="mb-4">
          Welcome to our application. By using this service, you agree to the following terms and conditions. If you do not agree with these terms, please do not use the application.
        </p>
  
        <h2 className="text-xl font-semibold mb-2">Use of the Service</h2>
        <p className="mb-4">
          This application is provided as-is and is intended for informational or utility purposes only. You agree to use the service lawfully and respectfully.
        </p>
  
        <h2 className="text-xl font-semibold mb-2">Authentication</h2>
        <p className="mb-4">
          Authentication is handled via Google Sign-In, managed through AWS Cognito. We do not store or access your personal information beyond verifying your login session.
        </p>
  
        <h2 className="text-xl font-semibold mb-2">Limitation of Liability</h2>
        <p className="mb-4">
          We are not liable for any damages or losses resulting from your use of this service. The app is provided without warranty of any kind.
        </p>
  
        <h2 className="text-xl font-semibold mb-2">Changes to These Terms</h2>
        <p className="mb-4">
          We reserve the right to update or modify these Terms of Service at any time. Continued use of the service after changes constitutes acceptance of the new terms.
        </p>
  
        <h2 className="text-xl font-semibold mb-2">Contact</h2>
        <p className="mb-4">
          If you have any questions or concerns about these terms, feel free to contact us at <a href="mailto:support@mongoagent.com" className="underline text-blue-600">support@mongoagent.com</a>.
        </p>
  
        <p className="text-sm text-gray-500 mt-8">Last updated: April 2, 2025</p>
      </div>
    );
  }
  