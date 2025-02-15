import { Link } from "react-router-dom";

function LandingPage() {
    return (
        <div className="flex flex-col items-center justify-center min-h-screen">
            <h1 className="text-4xl font-bold">Welcome to Savings Tracker!</h1>
            <p className="mt-4 text-lg">Track your finances and save more.</p>
            <div className="mt-6">
                <Link to="/login" className="px-4 py-2 bg-blue-500 text-white rounded-md">
                    Go to login
                </Link>
                <br></br>
                <Link to="/signup" className="px-4 py-2 bg-blue-500 text-white rounded-md">
                    Go to signup
                </Link>
            </div>
        </div>
    );
}

export default LandingPage;
