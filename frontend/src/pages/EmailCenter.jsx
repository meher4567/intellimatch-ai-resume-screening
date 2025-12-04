import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { Mail, Send, FileText, History, Plus, Edit, Trash2, Eye } from 'lucide-react';
import { Card, Button, Badge, Modal, EmptyState } from '../components';

function EmailCenter() {
  const [activeTab, setActiveTab] = useState('compose'); // compose, templates, history
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);

  const emailTemplates = [
    {
      id: 1,
      name: 'Interview Invitation',
      subject: 'Interview Invitation - {position}',
      body: 'Dear {candidate_name},\n\nWe are pleased to invite you for an interview for the {position} position...'
    },
    {
      id: 2,
      name: 'Application Received',
      subject: 'Application Received - {position}',
      body: 'Dear {candidate_name},\n\nThank you for applying to {position}. We have received your application...'
    },
    {
      id: 3,
      name: 'Rejection Letter',
      subject: 'Update on your application',
      body: 'Dear {candidate_name},\n\nThank you for your interest in the {position} position...'
    },
    {
      id: 4,
      name: 'Offer Letter',
      subject: 'Job Offer - {position}',
      body: 'Dear {candidate_name},\n\nCongratulations! We are pleased to offer you the position of {position}...'
    },
  ];

  const emailHistory = [
    {
      id: 1,
      to: 'john.doe@example.com',
      subject: 'Interview Invitation - Senior Software Engineer',
      sent_at: '2025-11-23T10:30:00',
      status: 'sent'
    },
    {
      id: 2,
      to: 'alice.smith@example.com',
      subject: 'Application Received - Product Manager',
      sent_at: '2025-11-22T14:15:00',
      status: 'sent'
    },
  ];

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center mb-6">
          <Mail className="mr-3 text-blue-600" />
          Email Center
        </h1>

        {/* Tabs */}
        <div className="flex space-x-2 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('compose')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'compose'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Send className="w-4 h-4 inline mr-2" />
            Compose
          </button>
          <button
            onClick={() => setActiveTab('templates')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'templates'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <FileText className="w-4 h-4 inline mr-2" />
            Templates ({emailTemplates.length})
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'history'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <History className="w-4 h-4 inline mr-2" />
            History ({emailHistory.length})
          </button>
        </div>
      </div>

      {/* Content */}
      {activeTab === 'compose' && <ComposeEmail templates={emailTemplates} />}
      {activeTab === 'templates' && (
        <TemplatesTab
          templates={emailTemplates}
          onNew={() => setShowTemplateModal(true)}
          onEdit={(template) => {
            setSelectedTemplate(template);
            setShowTemplateModal(true);
          }}
        />
      )}
      {activeTab === 'history' && <HistoryTab history={emailHistory} />}

      {/* Template Modal */}
      {showTemplateModal && (
        <TemplateModal
          template={selectedTemplate}
          onClose={() => {
            setShowTemplateModal(false);
            setSelectedTemplate(null);
          }}
          onSave={() => {
            setShowTemplateModal(false);
            setSelectedTemplate(null);
            toast.success('Template saved successfully!');
          }}
        />
      )}
    </div>
  );
}

// Compose Email Component
function ComposeEmail({ templates }) {
  const { register, handleSubmit, setValue } = useForm();
  const [selectedTemplate, setSelectedTemplate] = useState('');

  const onSubmit = (data) => {
    toast.success('Email sent successfully!');
  };

  const handleTemplateSelect = (templateId) => {
    const template = templates.find(t => t.id === parseInt(templateId));
    if (template) {
      setValue('subject', template.subject);
      setValue('body', template.body);
      setSelectedTemplate(templateId);
    }
  };

  return (
    <Card>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Use Template (optional)
          </label>
          <select
            value={selectedTemplate}
            onChange={(e) => handleTemplateSelect(e.target.value)}
            className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
          >
            <option value="">Select a template...</option>
            {templates.map(template => (
              <option key={template.id} value={template.id}>
                {template.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            To (Email Address) *
          </label>
          <input
            type="email"
            {...register('to', { required: true })}
            className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
            placeholder="candidate@example.com"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Subject *
          </label>
          <input
            type="text"
            {...register('subject', { required: true })}
            className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
            placeholder="Email subject"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Message *
          </label>
          <textarea
            {...register('body', { required: true })}
            rows={12}
            className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none font-mono text-sm"
            placeholder="Type your message here...\n\nAvailable variables:\n{candidate_name}\n{position}\n{company_name}"
          />
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            <strong>Tip:</strong> Use variables like {'{candidate_name}'} and {'{position}'} to personalize your emails.
          </p>
        </div>

        <div className="flex justify-end space-x-3">
          <Button type="button" variant="outline">
            Save Draft
          </Button>
          <Button type="submit" icon={Send}>
            Send Email
          </Button>
        </div>
      </form>
    </Card>
  );
}

// Templates Tab Component
function TemplatesTab({ templates, onNew, onEdit }) {
  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <p className="text-gray-600">Manage your email templates</p>
        <Button onClick={onNew} icon={Plus} size="sm">
          New Template
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {templates.map(template => (
          <Card key={template.id}>
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">{template.name}</h3>
                <p className="text-sm text-gray-600">{template.subject}</p>
              </div>
              <FileText className="w-5 h-5 text-blue-600" />
            </div>
            <p className="text-sm text-gray-700 mb-4 line-clamp-3">{template.body}</p>
            <div className="flex space-x-2">
              <Button variant="outline" size="sm" onClick={() => onEdit(template)} icon={Edit}>
                Edit
              </Button>
              <Button variant="outline" size="sm" icon={Eye}>
                Preview
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

// History Tab Component
function HistoryTab({ history }) {
  return (
    <div>
      <p className="text-gray-600 mb-4">Recent sent emails</p>
      {history.length > 0 ? (
        <div className="space-y-3">
          {history.map(email => (
            <Card key={email.id}>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <Mail className="w-5 h-5 text-blue-600" />
                    <h3 className="font-semibold text-gray-900">{email.subject}</h3>
                    <Badge variant="success">Sent</Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-1">To: {email.to}</p>
                  <p className="text-xs text-gray-500">
                    {new Date(email.sent_at).toLocaleString()}
                  </p>
                </div>
                <Button variant="outline" size="sm" icon={Eye}>
                  View
                </Button>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={Mail}
          title="No emails sent yet"
          description="Compose your first email to get started."
        />
      )}
    </div>
  );
}

// Template Modal Component
function TemplateModal({ template, onClose, onSave }) {
  const { register, handleSubmit } = useForm({
    defaultValues: template || {},
  });

  const onSubmit = (data) => {
    onSave(data);
  };

  return (
    <Modal
      isOpen={true}
      onClose={onClose}
      title={template ? 'Edit Template' : 'New Template'}
      size="lg"
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Template Name *
          </label>
          <input
            {...register('name', { required: true })}
            className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
            placeholder="e.g., Interview Invitation"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Subject Line *
          </label>
          <input
            {...register('subject', { required: true })}
            className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
            placeholder="Email subject"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Email Body *
          </label>
          <textarea
            {...register('body', { required: true })}
            rows={10}
            className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none font-mono text-sm"
            placeholder="Email content..."
          />
        </div>

        <div className="flex justify-end space-x-3 pt-4">
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit">
            Save Template
          </Button>
        </div>
      </form>
    </Modal>
  );
}

export default EmailCenter;
