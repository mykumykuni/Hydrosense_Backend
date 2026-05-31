from rest_framework import serializers
from .models import Report, ReportReply, REPORT_SUBJECT_DEFAULTS


class ReportReplySerializer(serializers.ModelSerializer):
    author_role = serializers.CharField(source='author.role', read_only=True)

    class Meta:
        model = ReportReply
        fields = ['id', 'report', 'author', 'author_email', 'author_role', 'message', 'created_at']
        read_only_fields = ['id', 'author', 'author_email', 'author_role', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['author'] = user
        validated_data['author_email'] = user.email
        return super().create(validated_data)


class ReportSerializer(serializers.ModelSerializer):
    replies = ReportReplySerializer(many=True, read_only=True)

    class Meta:
        model = Report
        fields = [
            'id', 'type', 'priority', 'subject', 'message', 'status',
            'submitted_by', 'submitted_by_email', 'replies',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'submitted_by', 'submitted_by_email', 'created_at', 'updated_at']

    def validate(self, data):
        report_type = data.get('type', getattr(self.instance, 'type', None))
        if report_type != 'custom' and not data.get('subject'):
            data['subject'] = REPORT_SUBJECT_DEFAULTS.get(report_type, report_type.replace('_', ' ').title())
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['submitted_by'] = user
        validated_data['submitted_by_email'] = user.email
        return super().create(validated_data)
