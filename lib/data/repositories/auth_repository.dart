import '../models/auth_request.dart';
import '../models/auth_response.dart';
import '../models/user_model.dart';
import '../services/api_service.dart';
import '../services/storage_service.dart';

/// Repository for authentication operations
class AuthRepository {
  /// Update current user profile
  Future<User> updateProfile(Map<String, dynamic> updateData) async {
    return await _apiService.updateProfile(updateData);
  }

  final ApiService _apiService;

  AuthRepository(this._apiService);

  /// Register new user
  Future<AuthResponse> register(RegisterRequest request) async {
    final response = await _apiService.register(request);

    // Store tokens
    await StorageService.saveTokens(
      accessToken: response.token.accessToken,
      refreshToken: response.token.refreshToken,
      userId: response.user.id,
    );

    return response;
  }

  /// Login user
  Future<AuthResponse> login(LoginRequest request) async {
    final response = await _apiService.login(request);

    // Store tokens
    await StorageService.saveTokens(
      accessToken: response.token.accessToken,
      refreshToken: response.token.refreshToken,
      userId: response.user.id,
    );

    return response;
  }

  /// Get current user
  Future<User> getCurrentUser() async {
    return await _apiService.getCurrentUser();
  }

  /// Logout
  Future<void> logout() async {
    await StorageService.clearAll();
  }

  /// Check if user is logged in
  Future<bool> isLoggedIn() async {
    return await StorageService.isLoggedIn();
  }
}
