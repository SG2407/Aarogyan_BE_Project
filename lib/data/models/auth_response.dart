import 'package:json_annotation/json_annotation.dart';
import 'user_model.dart';
import 'token_model.dart';

part 'auth_response.g.dart';

@JsonSerializable()
class AuthResponse {
  final User user;
  final Token token;

  AuthResponse({required this.user, required this.token});

  factory AuthResponse.fromJson(Map<String, dynamic> json) =>
      _$AuthResponseFromJson(json);
  Map<String, dynamic> toJson() => _$AuthResponseToJson(this);
}
