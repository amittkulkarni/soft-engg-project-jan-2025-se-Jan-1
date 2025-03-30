<template>
    <div class="register-page">
        <!-- Left Section -->
        <div class="left-section">
            <img src="https://cdn-icons-png.flaticon.com/512/3976/3976631.png" alt="Education Icon" class="floating-icon"/>
            <h1 class="floating-title">Welcome to SEEK</h1>
            <h2 class="floating-text">Your gateway to personalized education.</h2>
            <h2 class="floating-text">Join us and embark on a journey of</h2>
            <h2 class="floating-text">growth and success!</h2>
        </div>

        <!-- Right Section -->
        <div class="right-section">
            <div class="form-container">
                <h1>Create an Account</h1>
                <p>Join us to get started</p>
                <form @submit.prevent="register">
                    <div class="form-group">
                        <label for="name">Full Name</label>
                        <input type="text" id="name" v-model="name" placeholder="Enter your full name" required/>
                    </div>
                    <div class="form-group">
                        <label for="email">Email</label>
                        <input type="email" id="email" v-model="email" placeholder="Enter your email" required/>
                    </div>
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" id="password" v-model="password" placeholder="Enter your password" required/>
                    </div>
                    <button type="submit" class="btn">Register</button>
                    <!-- Divider -->
                    <div class="divider">
                        <span class="divider-line"></span>
                        <span class="divider-text">OR</span>
                        <span class="divider-line"></span>
                    </div>

                    <!-- Google Login Button -->
                    <GoogleLogin
                        :callback="handleGoogleCallback"
                        popup-type="TOKEN"
                    >
                        <button type="button" class="google-btn">
                            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 300 300" id="google">
                                <path fill="#4285F4" d="M255.878 133.451c0-10.734-.871-18.567-2.756-26.69H130.55v48.448h71.947c-1.45 12.04-9.283 30.172-26.69 42.356l-.244 1.622 38.755 30.023 2.685.268c24.659-22.774 38.875-56.282 38.875-96.027"></path>
                                <path fill="#34A853" d="M130.55 261.1c35.248 0 64.839-11.605 86.453-31.622l-41.196-31.913c-11.024 7.688-25.82 13.055-45.257 13.055-34.523 0-63.824-22.773-74.269-54.25l-1.531.13-40.298 31.187-.527 1.465C35.393 231.798 79.49 261.1 130.55 261.1"></path>
                                <path fill="#FBBC05" d="M56.281 156.37c-2.756-8.123-4.351-16.827-4.351-25.82 0-8.994 1.595-17.697 4.206-25.82l-.073-1.73L15.26 71.312l-1.335.635C5.077 89.644 0 109.517 0 130.55s5.077 40.905 13.925 58.602l42.356-32.782"></path>
                                <path fill="#EB4335" d="M130.55 50.479c24.514 0 41.05 10.589 50.479 19.438l36.844-35.974C195.245 12.91 165.798 0 130.55 0 79.49 0 35.393 29.301 13.925 71.947l42.211 32.783c10.59-31.477 39.891-54.251 74.414-54.251"></path>
                            </svg>
                            Sign Up with Google
                        </button>
                    </GoogleLogin>
                </form>
                <p>
                    Already have an account?
                    <router-link to="/login">Login</router-link>
                </p>
            </div>
        </div>
    </div>
</template>


<script>
import { GoogleLogin } from 'vue3-google-login'
import api from "@/services/api.js"
export default {
    name: "RegisterPage",
    components: { GoogleLogin },
    data() {
        return {
            name: "",
            email: "",
            password: "",
        };
    },
    mounted() {
        // Check if coming from another page within the app
        if (document.referrer.includes(window.location.origin)) {
            window.location.reload();
        }
    },
    methods: {
        async register() {
            try {
                // Send POST request to signup endpoint
                const response = await api.post('/signup', {
                    username: this.name,
                    email: this.email,
                    password: this.password,
                    role: 'student'
                });
                await this.$router.push("/course");
                alert(response.data.message);
            } catch(error) {
                // Handle errors
                if (error.response) {
                    // The request was made and the server responded with an error status
                    alert(error.response.data.message || "Registration failed");
                    console.error("Registration error:", error.response.data);
                } else if (error.request) {
                    // The request was made but no response was received
                    alert("No response from server. Please try again later.");
                    console.error("No response received:", error.request);
                } else {
                    // Something happened in setting up the request
                    alert("Error setting up request: " + error.message);
                    console.error("Request setup error:", error.message);
                }
            }
        },
        handleGoogleCallback(response) {
            const access_token = response.access_token;

            // Send the ID token to backend
            fetch('http://localhost:5000/google_signup', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 'access_token': access_token }),
                    credentials: 'include'
                })
                .then(response => {
                    return response.json().then(data => {
                        if (!response.ok) {
                            throw new Error(data.message || `Error: ${response.status}`);
                        }
                        return data;
                    });
                })
                .then(data => {
                    if (data.Success) {
                        // Store token for authenticated requests
                        localStorage.setItem('auth_token', data.access_token);
                        this.$router.push("/course");
                    } else {
                        alert(data.message || "Registration failed");
                    }
                })
                .catch(error => {
                    console.error("Fetch error:", error);
                    alert(`Authentication failed: ${error.message}`);
                });
        }
    }
};
</script>

<style scoped>

.register-page {
    display: flex;
    height: 100vh;
    font-family: Arial, sans-serif;
}

/* Left Section */
.left-section {
    flex: 1;
    background-color: #6c1b1b;
    background-image: radial-gradient(circle, rgba(255, 255, 255, 0.1) 10%, transparent 20%),
        radial-gradient(circle, rgba(255, 255, 255, 0.1) 10%, transparent 20%);
    background-size: 30px 30px;
    background-position: 0 0, 15px 15px;
    background-repeat: repeat;
    position: relative;
    overflow: hidden;
    color: white;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 2rem;
    text-align: center;
    overflow: hidden;
}


.floating-icon {
    width: 100px;
    height: 100px;
    margin-bottom: 20px;
    opacity: 0;
    animation: fadeIn 2s ease-in-out forwards;
    animation-delay: 0s;
}

.floating-title {
    opacity: 0;
    animation: fadeIn 2s ease-in-out forwards;
    animation-delay: 0.5s;
}

.floating-text {
    opacity: 0;
    animation: fadeIn 2s ease-in-out forwards;
    animation-delay: 1s;
}

/* Keyframes for the fadeIn animation */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Right Section */
.right-section {
    flex: 1;
    background-color: #f7f7f7;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 2rem;
}

/* Form Container */
.form-container {
    background-color: white;
    border: 2px solid #d3d3d3;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 400px;
    text-align: center;
}

.form-container h1 {
    font-size: 1.8rem;
    margin-bottom: 0.5rem;
    color: #6c1b1b;
}

.form-container p {
    font-size: 1rem;
    margin-bottom: 1.5rem;
    color: #555555;
}

.form-group {
    margin-bottom: 1rem;
    text-align: left;
}

label {
    display: block;
    font-weight: bold;
    margin-bottom: 0.3rem;
}

input {
    width: 100%;
    padding: 0.5rem;
    font-size: 1rem;
    border: 1px solid #ccc;
    border-radius: 8px;
    box-sizing: border-box;
}

input:focus {
    outline: none;
    border-color: #0047ab;
}

.btn {
    background-color: #6c1b1b;
    color: white;
    padding: 0.7rem 1rem;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    cursor: pointer;
    width: 100%;
}

.btn:hover {
    background-color: #990000;
}
.divider {
    display: flex;
    align-items: center;
    margin: 1.5rem 0;
}

.divider-line {
    flex: 1;
    height: 1px;
    background-color: #ddd;
}

.divider-text {
    padding: 0 1rem;
    color: #666;
    font-size: 0.9rem;
}

.google-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    padding: 0.7rem 1rem;
    background: #ffffff;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 1rem;
    color: #4285F4;
    cursor: pointer;
    transition: all 0.3s ease;
}

.google-btn:hover {
    background: #f8f9fa;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn {
    margin-bottom: 1rem;
}
</style>
