import 'package:flutter/material.dart';

class MedicalOnboardingModal extends StatelessWidget {
  final String question;
  final double completionScore;
  final Function(Map<String, dynamic>) onSubmit;
  final VoidCallback onSkip;
  final VoidCallback onClose;

  const MedicalOnboardingModal({
    required this.question,
    required this.completionScore,
    required this.onSubmit,
    required this.onSkip,
    required this.onClose,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    final TextEditingController answerController = TextEditingController();
    return AlertDialog(
      title: Text('Medical Onboarding'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text('Profile ${completionScore.toStringAsFixed(0)}% complete'),
          const SizedBox(height: 12),
          Text(question),
          const SizedBox(height: 12),
          TextField(
            controller: answerController,
            decoration: const InputDecoration(labelText: 'Your answer'),
          ),
        ],
      ),
      actions: [
        TextButton(onPressed: onSkip, child: const Text('Skip')),
        TextButton(
          onPressed: () {
            onSubmit({'response': answerController.text});
          },
          child: const Text('Submit'),
        ),
        TextButton(onPressed: onClose, child: const Text('Close')),
      ],
    );
  }
}
