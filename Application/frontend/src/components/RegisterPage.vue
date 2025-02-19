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
                    <button type="button" class="google-btn" @click="handleGoogleSignup">
                      <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 300 300" id="google">
                    <path fill="#4285F4" d="M255.878 133.451c0-10.734-.871-18.567-2.756-26.69H130.55v48.448h71.947c-1.45 12.04-9.283 30.172-26.69 42.356l-.244 1.622 38.755 30.023 2.685.268c24.659-22.774 38.875-56.282 38.875-96.027"></path>
                    <path fill="#34A853" d="M130.55 261.1c35.248 0 64.839-11.605 86.453-31.622l-41.196-31.913c-11.024 7.688-25.82 13.055-45.257 13.055-34.523 0-63.824-22.773-74.269-54.25l-1.531.13-40.298 31.187-.527 1.465C35.393 231.798 79.49 261.1 130.55 261.1"></path>
                    <path fill="#FBBC05" d="M56.281 156.37c-2.756-8.123-4.351-16.827-4.351-25.82 0-8.994 1.595-17.697 4.206-25.82l-.073-1.73L15.26 71.312l-1.335.635C5.077 89.644 0 109.517 0 130.55s5.077 40.905 13.925 58.602l42.356-32.782"></path>
                    <path fill="#EB4335" d="M130.55 50.479c24.514 0 41.05 10.589 50.479 19.438l36.844-35.974C195.245 12.91 165.798 0 130.55 0 79.49 0 35.393 29.301 13.925 71.947l42.211 32.783c10.59-31.477 39.891-54.251 74.414-54.251"></path>
                  </svg>
                        Sign Up with Google
                    </button>
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
export default {
    name: "RegisterPage",
    data() {
        return {
            name: "",
            email: "",
            password: "",
        };
    },
    methods: {
        register() {
            alert("Registration successful!");
            this.$router.push("/course");
        },
        handleGoogleSignup() {
            this.$router.push("/course");
          }
    },
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
    /* Base dark red color */
    background-image: radial-gradient(circle, rgba(255, 255, 255, 0.1) 10%, transparent 20%),
        radial-gradient(circle, rgba(255, 255, 255, 0.1) 10%, transparent 20%);
    background-size: 30px 30px;
    background-position: 0 0, 15px 15px;
    /* Alternate dot pattern */
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
    /* Ensures no animation overflow */
}

.overlay-left,
.overlay-right {
    position: absolute;
    top: 0;
    bottom: 0;
    width: 200px;
    background: rgba(0, 0, 0, 0.2);
    /* Adjust transparency */
    border-radius: 50%;
}

.overlay-left {
    left: -100px;
}

.overlay-right {
    right: -100px;
}

.floating-icon {
    width: 100px;
    /* Set the size of the icon */
    height: 100px;
    margin-bottom: 20px;
    /* Add space below the icon */
    opacity: 0;
    animation: fadeIn 2s ease-in-out forwards;
    animation-delay: 0s;
    /* Same as the title to float together */
}

.floating-title {
    opacity: 0;
    animation: fadeIn 2s ease-in-out forwards;
    animation-delay: 0.5s;
    /* Slight delay after the icon */
}

.floating-text {
    opacity: 0;
    animation: fadeIn 2s ease-in-out forwards;
    animation-delay: 1s;
    /* Staggered delay for floating text */
}

/* Keyframes for the fadeIn animation */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
        /* Start slightly below */
    }

    to {
        opacity: 1;
        transform: translateY(0);
        /* Move into place */
    }
}

/* Right Section */
.right-section {
    flex: 1;
    background-color: #f7f7f7;
    /* Soft light grey background */
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
    /* Match first page color */
}

.form-container p {
    font-size: 1rem;
    margin-bottom: 1.5rem;
    color: #555555;
    /* Subtle grey text */
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
    /* Slightly curved fields */
    box-sizing: border-box;
}

input:focus {
    outline: none;
    border-color: #0047ab;
    /* Highlight color */
}

.btn {
    background-color: #6c1b1b;
    /* Match first page button color */
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
    /* Slightly darker blue on hover */
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
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }

  /* Adjust existing button spacing */
  .btn {
    margin-bottom: 1rem;
  }
</style>
