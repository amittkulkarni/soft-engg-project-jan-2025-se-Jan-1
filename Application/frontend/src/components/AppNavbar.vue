<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom">
    <div class="container-fluid">
      <!-- Left side: Logo + Subject Name -->
      <a class="navbar-brand d-flex align-items-center" href="#">
        <img :src="logoPath" alt="Institute Logo" width="120" height="40" class="me-2" />
        <span class="course-title">Jan 2025 - MLP</span>
      </a>

      <!-- Right side: Support, Profile icons, etc. -->
      <ul class="navbar-nav ms-auto">
        <li class="nav-item me-3">
          <a class="nav-link" href="#">
            <i class="bi bi-question-circle"></i>
            Support
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="#">
            <i class="bi bi-person-circle"></i>
            Profile
          </a>
        </li>
      </ul>
    </div>
  </nav>
</template>

<script>
import logoPath from '@/assets/iitm-logo@3x.png';

export default {
  name: 'AppNavbar',
  data() {
    return {
      logoPath,
    };
  },
};
</script>

<style scoped>
.course-title {
  color: #606060;
  letter-spacing: .00178571429em;
  font-size: 14px;
  line-height: 24px;
  font-weight: 600;
  background: #f7f7fa;
  padding: 4px 10px;
  border-radius: 4px;
}
</style>
