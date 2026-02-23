import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/services/chat_service.dart';
import '../data/repositories/chat_repository.dart';
import 'package:dio/dio.dart';
import '../data/services/storage_service.dart';

final dioProvider = Provider<Dio>((ref) {
  final dio = Dio();
  dio.options.baseUrl =
      'https://aarogyan-be-project-1.onrender.com/api/v1'; // Use deployed Render backend for production

  dio.interceptors.add(
    InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await StorageService.getAccessToken();
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
    ),
  );
  return dio;
});

final chatServiceProvider = Provider<ChatService>((ref) {
  final dio = ref.watch(dioProvider);
  return ChatService(dio);
});

final chatRepositoryProvider = Provider<ChatRepository>((ref) {
  final service = ref.watch(chatServiceProvider);
  return ChatRepository(service);
});
