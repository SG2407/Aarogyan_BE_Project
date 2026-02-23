// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

User _$UserFromJson(Map<String, dynamic> json) => User(
  id: json['id'] as String,
  email: json['email'] as String,
  name: json['name'] as String,
  age: (json['age'] as num?)?.toInt(),
  gender: json['gender'] as String?,
  phone: json['phone'] as String?,
  emergencyContact: json['emergency_contact'] as String?,
  createdAt: json['created_at'] as String,
);

Map<String, dynamic> _$UserToJson(User instance) => <String, dynamic>{
  'id': instance.id,
  'email': instance.email,
  'name': instance.name,
  'age': instance.age,
  'gender': instance.gender,
  'phone': instance.phone,
  'emergency_contact': instance.emergencyContact,
  'created_at': instance.createdAt,
};
