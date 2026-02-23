import '../services/chat_service.dart';
import '../models/chat_message.dart';

class ChatRepository {
  final ChatService _service;
  ChatRepository(this._service);

  Future<List<ChatMessageModel>> fetchMessages(String chatId) =>
      _service.fetchMessages(chatId);
  Future<void> sendMessage(String chatId, String content) =>
      _service.sendMessage(chatId, content);
  Future<String> createChat([String? title]) => _service.createChat(title);
  Future<void> deleteChat(String chatId) => _service.deleteChat(chatId);
}
