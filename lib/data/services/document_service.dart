import 'package:dio/dio.dart';
import '../../core/config/api_config.dart';

class DocumentService {
  final Dio _dio;

  DocumentService([Dio? dio])
    : _dio =
          dio ??
          Dio(
            BaseOptions(
              baseUrl: ApiConfig.baseUrl,
              connectTimeout: ApiConfig.connectTimeout,
              receiveTimeout: ApiConfig.receiveTimeout,
              headers: {'Content-Type': 'application/json'},
            ),
          );

  Future<List<dynamic>> listDocuments() async {
    final response = await _dio.get('/documents/list');
    return response.data as List<dynamic>;
  }

  Future<Map<String, dynamic>> getDocument(String docId) async {
    final response = await _dio.get('/documents/$docId');
    return response.data as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> uploadDocument({
    required String filePath,
    required String fileName,
    required String userId,
  }) async {
    final formData = FormData.fromMap({
      'file': await MultipartFile.fromFile(filePath, filename: fileName),
      'user_id': userId,
    });
    final response = await _dio.post('/documents/upload', data: formData);
    return response.data as Map<String, dynamic>;
  }
}
