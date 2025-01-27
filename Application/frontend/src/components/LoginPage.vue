<template>
<div class="login-page">
    <!-- Left Section -->
    <div class="left-section">
        <img src="https://cdn-icons-png.flaticon.com/512/3976/3976631.png" alt="Education Icon" class="floating-icon" />
        <h1 class="floating-title">Welcome Back to Education Navigator</h1>
        <h2 class="floating-text">Empowering your learning journey.</h2>
        <h2 class="floating-text">Login to access your dashboard!</h2>
    </div>

    <!-- Right Section -->
    <div class="right-section">
        <div class="form-container">
            <h1>Welcome Back</h1>
            <p>Please login to continue</p>
            <form @submit.prevent="login">
                <div class="form-group">
                    <label for="email">Email</label>
                    <input type="email" id="email" v-model="email" placeholder="Enter your email" required />
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" v-model="password" placeholder="Enter your password" required />
                </div>
                <button type="submit" class="btn">Login</button>
            </form>
            <p>
                Don't have an account?
                <router-link to="/register">Register</router-link>
            </p>
        </div>
    </div>
</div>
</template>

  
<script>
export default {
    name: "LoginPage",
    data() {
        return {
            email: "",
            password: "",
        };
    },
    methods: {
        login() {
            alert("login successful!");
            this.$router.push("/course");
        },
    },
};
</script>

  
<style scoped>
.login-page {
    display: flex;
    height: 100vh;
    font-family: Arial, sans-serif;
}

/* Left Section */
.left-section {
    flex: 1;
    background-color: #6c1b1b;
    /* Base dark red color */
    background-image:
        radial-gradient(circle, rgba(255, 255, 255, 0.1) 10%, transparent 20%),
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

.router-link {
    color: #0047ab;
    text-decoration: none;
}

.router-link:hover {
    text-decoration: underline;
}
</style>
