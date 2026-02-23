import 'package:json_annotation/json_annotation.dart';

part 'chat_message.g.dart';


@JsonSerializable()
class ChatMessageModel {
  final String id;
  @JsonKey(name: 'chat_id')
  final String chatId;
  final String sender;
  final String content;
  @JsonKey(name: 'created_at')
  final DateTime createdAt;

  ChatMessageModel({
    required this.id,
    required this.chatId,
    required this.sender,
    required this.content,
    required this.createdAt,
  });

  factory ChatMessageModel.fromJson(Map<String, dynamic> json) =>
      _$ChatMessageModelFromJson(json);
  Map<String, dynamic> toJson() => _$ChatMessageModelToJson(this);
}
