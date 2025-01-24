<template>
<div class="home-page">
    <header class="header">
        <h1>Education Navigator</h1>
    </header>
    <main class="main-content">
        <div class="content-box">
            <h2>Welcome to Education Navigator</h2>
            <p>The Ultimate Classroom for One Course</p>
            <button @click="signIn">Register</button>
        </div>
    </main>
    <footer class="footer">
        <p>© 2025 Software Engineering Project Team 1 | Jan 2025 Term. All rights reserved.</p>
    </footer>
</div>
</template>

<script>
export default {
    name: "HomePage",
    methods: {
        signIn() {
            this.$router.push("/register");
        },
    },
};
</script>

<style scoped>
.home-page {
    text-align: center;
    font-family: Arial, sans-serif;
    color: #333;
    display: flex;
    flex-direction: column;
    height: 100vh;
}

/* Header Styling */
.header {
    background-color: #6c1b1b;
    color: white;
    padding: 10px 0;
}

/* Main Content Styling */
.main-content {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
}

.content-box {
    background-color: white;
    border: 2px solid #ccc;
    border-radius: 12px;
    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
    padding: 40px 30px;
    text-align: center;
    max-width: 500px;
    width: 100%;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    /* Add transition for smooth animation */
}

.content-box h2 {
    font-size: 2.5em;
    margin-bottom: 20px;
    color: #6c1b1b;
}

.content-box p {
    font-size: 1.2em;
    margin-bottom: 30px;
    color: #555;
}

button {
    background-color: #6c1b1b;
    color: white;
    border: none;
    padding: 10px 20px;
    font-size: 1em;
    cursor: pointer;
    border-radius: 5px;
}

button:hover {
    background-color: #990000;
}

/* Hover Animation for Content Box */
.content-box:hover {
    transform: translateY(-10px);
    /* Moves the box slightly upward */
    box-shadow: 0px 8px 16px rgba(0, 0, 0, 0.2);
    /* Adds a more prominent shadow */
}

/* Footer Styling */
.footer {
    background-color: #333;
    color: white;
    padding: 10px 0;
}
</style>
