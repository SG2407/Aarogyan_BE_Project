/// API Configuration
class ApiConfig {
  // Change this to your backend URL
  // For local testing on physical device: use your computer's IP
  // For local testing on emulator: use 10.0.2.2 (Android) or localhost (iOS)
  static const String baseUrl = 'https://aarogyan-be-project-1.onrender.com/api/v1';

  // Endpoints
  static const String register = '/auth/register';
  static const String login = '/auth/login';
  static const String refresh = '/auth/refresh';
  static const String me = '/auth/me';

  // Timeouts
  static const Duration connectTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
}
