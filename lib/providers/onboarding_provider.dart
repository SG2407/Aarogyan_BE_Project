import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/services/api_service.dart';

final onboardingProvider = StateNotifierProvider<OnboardingNotifier, OnboardingState>((ref) {
  return OnboardingNotifier(ApiService());
});

class OnboardingState {
  final bool showOnboarding;
  final double completionScore;
  final String? currentQuestion;
  final bool isLoading;
  final Map<String, dynamic> profile;

  OnboardingState({
    required this.showOnboarding,
    required this.completionScore,
    this.currentQuestion,
    this.isLoading = false,
    this.profile = const {},
  });

  OnboardingState copyWith({
    bool? showOnboarding,
    double? completionScore,
    String? currentQuestion,
    bool? isLoading,
    Map<String, dynamic>? profile,
  }) {
    return OnboardingState(
      showOnboarding: showOnboarding ?? this.showOnboarding,
      completionScore: completionScore ?? this.completionScore,
      currentQuestion: currentQuestion ?? this.currentQuestion,
      isLoading: isLoading ?? this.isLoading,
      profile: profile ?? this.profile,
    );
  }
}

class OnboardingNotifier extends StateNotifier<OnboardingState> {
  final ApiService apiService;
  OnboardingNotifier(this.apiService)
      : super(OnboardingState(showOnboarding: false, completionScore: 0));

  Future<void> checkProfileCompletion(String userId) async {
    state = state.copyWith(isLoading: true);
    final resp = await apiService.getMedicalProfile(userId);
    final score = resp['completion_score'] as double;
    final show = score < 70;
    state = state.copyWith(
      showOnboarding: show,
      completionScore: score,
      profile: resp['profile'] as Map<String, dynamic>,
      currentQuestion: resp['next_question'] as String?,
      isLoading: false,
    );
  }

  Future<void> submitAnswer(String userId, Map<String, dynamic> answer) async {
    state = state.copyWith(isLoading: true);
    final resp = await apiService.submitOnboardingAnswer(userId, answer);
    final score = resp['completion_score'] as double;
    final show = score < 70;
    state = state.copyWith(
      showOnboarding: show,
      completionScore: score,
      profile: resp['profile'] as Map<String, dynamic>,
      currentQuestion: resp['next_question'] as String?,
      isLoading: false,
    );
  }

  Future<void> skipQuestion(String userId) async {
    state = state.copyWith(isLoading: true);
    final resp = await apiService.skipOnboardingQuestion(userId);
    state = state.copyWith(
      currentQuestion: resp['next_question'] as String?,
      isLoading: false,
    );
  }

  void closeOnboarding() {
    state = state.copyWith(showOnboarding: false);
  }
}
