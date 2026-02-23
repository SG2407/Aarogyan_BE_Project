import 'package:dio/dio.dart';
import '../models/chat_message.dart';

class ChatService {
  final Dio _dio;
  ChatService(this._dio);

  Future<List<ChatMessageModel>> fetchMessages(String chatId) async {
    final response = await _dio.get('/ai/chats/$chatId/messages');
    final data = response.data['messages'] as List;
    return data.map((e) => ChatMessageModel.fromJson(e)).toList();
  }

  Future<void> sendMessage(String chatId, String content) async {
    await _dio.post(
      '/ai/chats/$chatId/messages',
      data: {'chat_id': chatId, 'content': content, 'sender': 'user'},
    );
  }

  Future<String> createChat([String? title]) async {
    final response = await _dio.post(
      '/ai/chats',
      data: {if (title != null) 'title': title},
    );
    return response.data['id'] as String;
  }

  Future<void> deleteChat(String chatId) async {
    await _dio.delete('/ai/chats/$chatId');
  }
}
