import 'package:json_annotation/json_annotation.dart';

part 'user_update_request.g.dart';

@JsonSerializable()
class UserUpdateRequest {
  final String? name;
  final int? age;
  final String? gender;
  final String? phone;
  @JsonKey(name: 'emergency_contact')
  final String? emergencyContact;

  UserUpdateRequest({
    this.name,
    this.age,
    this.gender,
    this.phone,
    this.emergencyContact,
  });

  factory UserUpdateRequest.fromJson(Map<String, dynamic> json) =>
      _$UserUpdateRequestFromJson(json);
  Map<String, dynamic> toJson() => _$UserUpdateRequestToJson(this);
}
