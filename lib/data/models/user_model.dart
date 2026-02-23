import 'package:json_annotation/json_annotation.dart';

part 'user_model.g.dart';

@JsonSerializable()
class User {
  final String id;
  final String email;
  final String name;
  final int? age;
  final String? gender;
  final String? phone;
  @JsonKey(name: 'emergency_contact')
  final String? emergencyContact;
  @JsonKey(name: 'created_at')
  final String createdAt;

  User({
    required this.id,
    required this.email,
    required this.name,
    this.age,
    this.gender,
    this.phone,
    this.emergencyContact,
    required this.createdAt,
  });

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
  Map<String, dynamic> toJson() => _$UserToJson(this);
}
