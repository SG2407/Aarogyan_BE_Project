class RegisterRequest {
  final String email;
  final String password;
  final String name;
  final int? age;
  final String? gender;
  final String? phone;
  final String? emergencyContact;

  RegisterRequest({
    required this.email,
    required this.password,
    required this.name,
    this.age,
    this.gender,
    this.phone,
    this.emergencyContact,
  });

  Map<String, dynamic> toJson() {
    return {
      'email': email,
      'password': password,
      'name': name,
      if (age != null) 'age': age,
      if (gender != null) 'gender': gender,
      if (phone != null) 'phone': phone,
      if (emergencyContact != null) 'emergency_contact': emergencyContact,
    };
  }
}

class LoginRequest {
  final String email;
  final String password;

  LoginRequest({required this.email, required this.password});

  Map<String, dynamic> toJson() {
    return {'email': email, 'password': password};
  }
}
