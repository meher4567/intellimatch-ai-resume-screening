import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { Settings as SettingsIcon, Sliders, Database, User, Bell, Shield, Save } from 'lucide-react';
import { Card, Button, Badge, ProgressBar } from '../components';

function Settings() {
  const [activeSection, setActiveSection] = useState('scoring');

  const sections = [
    { id: 'scoring', label: 'Scoring Configuration', icon: Sliders },
    { id: 'skills', label: 'Skill Taxonomy', icon: Database },
    { id: 'profile', label: 'User Profile', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Shield },
  ];

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-gray-900 flex items-center mb-8">
        <SettingsIcon className="mr-3 text-blue-600" />
        Settings
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <Card>
            <nav className="space-y-2">
              {sections.map(section => {
                const Icon = section.icon;
                return (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                      activeSection === section.id
                        ? 'bg-blue-50 text-blue-700 font-medium'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span>{section.label}</span>
                  </button>
                );
              })}
            </nav>
          </Card>
        </div>

        {/* Content */}
        <div className="lg:col-span-3">
          {activeSection === 'scoring' && <ScoringSettings />}
          {activeSection === 'skills' && <SkillTaxonomySettings />}
          {activeSection === 'profile' && <ProfileSettings />}
          {activeSection === 'notifications' && <NotificationSettings />}
          {activeSection === 'security' && <SecuritySettings />}
        </div>
      </div>
    </div>
  );
}

// Scoring Configuration
function ScoringSettings() {
  const { register, handleSubmit } = useForm({
    defaultValues: {
      skills_weight: 40,
      experience_weight: 30,
      education_weight: 20,
      other_weight: 10,
    },
  });

  const onSubmit = (data) => {
    toast.success('Scoring configuration saved!');
  };

  return (
    <Card>
      <h2 className="text-xl font-bold text-gray-900 mb-4">Scoring Configuration</h2>
      <p className="text-gray-600 mb-6">
        Adjust the weights for different criteria in candidate scoring. Total must equal 100%.
      </p>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div>
          <div className="flex justify-between mb-2">
            <label className="text-sm font-medium text-gray-700">Skills Match</label>
            <span className="text-sm font-medium text-blue-600">{40}%</span>
          </div>
          <input
            type="range"
            {...register('skills_weight')}
            min="0"
            max="100"
            className="w-full"
          />
          <ProgressBar value={40} color="blue" showPercentage={false} />
        </div>

        <div>
          <div className="flex justify-between mb-2">
            <label className="text-sm font-medium text-gray-700">Experience</label>
            <span className="text-sm font-medium text-green-600">{30}%</span>
          </div>
          <input
            type="range"
            {...register('experience_weight')}
            min="0"
            max="100"
            className="w-full"
          />
          <ProgressBar value={30} color="green" showPercentage={false} />
        </div>

        <div>
          <div className="flex justify-between mb-2">
            <label className="text-sm font-medium text-gray-700">Education</label>
            <span className="text-sm font-medium text-purple-600">{20}%</span>
          </div>
          <input
            type="range"
            {...register('education_weight')}
            min="0"
            max="100"
            className="w-full"
          />
          <ProgressBar value={20} color="purple" showPercentage={false} />
        </div>

        <div>
          <div className="flex justify-between mb-2">
            <label className="text-sm font-medium text-gray-700">Other Factors</label>
            <span className="text-sm font-medium text-yellow-600">{10}%</span>
          </div>
          <input
            type="range"
            {...register('other_weight')}
            min="0"
            max="100"
            className="w-full"
          />
          <ProgressBar value={10} color="yellow" showPercentage={false} />
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            <strong>Total:</strong> 100%
          </p>
        </div>

        <div className="flex justify-end">
          <Button type="submit" icon={Save}>
            Save Configuration
          </Button>
        </div>
      </form>
    </Card>
  );
}

// Skill Taxonomy Settings
function SkillTaxonomySettings() {
  const skillCategories = [
    { name: 'Programming Languages', count: 25 },
    { name: 'Frameworks & Libraries', count: 42 },
    { name: 'Databases', count: 15 },
    { name: 'Cloud & DevOps', count: 18 },
    { name: 'Soft Skills', count: 20 },
  ];

  return (
    <Card>
      <h2 className="text-xl font-bold text-gray-900 mb-4">Skill Taxonomy</h2>
      <p className="text-gray-600 mb-6">
        Manage your organization's skill taxonomy and categories.
      </p>

      <div className="space-y-3 mb-6">
        {skillCategories.map((category, index) => (
          <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <h3 className="font-medium text-gray-900">{category.name}</h3>
              <p className="text-sm text-gray-600">{category.count} skills</p>
            </div>
            <Button variant="outline" size="sm">
              Manage
            </Button>
          </div>
        ))}
      </div>

      <Button icon={Database}>
        Add New Category
      </Button>
    </Card>
  );
}

// Profile Settings
function ProfileSettings() {
  const { register, handleSubmit } = useForm({
    defaultValues: {
      name: 'John Doe',
      email: 'john.doe@company.com',
      company: 'TechCorp Inc.',
      role: 'HR Manager',
    },
  });

  const onSubmit = (data) => {
    toast.success('Profile updated!');
  };

  return (
    <Card>
      <h2 className="text-xl font-bold text-gray-900 mb-4">User Profile</h2>
      <p className="text-gray-600 mb-6">Manage your personal information and preferences.</p>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
            <input
              {...register('name')}
              className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              {...register('email')}
              className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Company</label>
            <input
              {...register('company')}
              className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
            <input
              {...register('role')}
              className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
            />
          </div>
        </div>

        <div className="flex justify-end">
          <Button type="submit" icon={Save}>
            Update Profile
          </Button>
        </div>
      </form>
    </Card>
  );
}

// Notification Settings
function NotificationSettings() {
  const [notifications, setNotifications] = useState({
    newResume: true,
    matchFound: true,
    interviewScheduled: true,
    emailSent: false,
    weeklyReport: true,
  });

  const handleToggle = (key) => {
    setNotifications(prev => ({ ...prev, [key]: !prev[key] }));
    toast.success('Notification preferences updated!');
  };

  return (
    <Card>
      <h2 className="text-xl font-bold text-gray-900 mb-4">Notification Preferences</h2>
      <p className="text-gray-600 mb-6">Choose what notifications you want to receive.</p>

      <div className="space-y-4">
        {[
          { key: 'newResume', label: 'New Resume Uploaded', description: 'Get notified when a new resume is added' },
          { key: 'matchFound', label: 'Match Found', description: 'Alert when a good candidate match is found' },
          { key: 'interviewScheduled', label: 'Interview Scheduled', description: 'Receive updates about scheduled interviews' },
          { key: 'emailSent', label: 'Email Sent', description: 'Confirmation when emails are successfully sent' },
          { key: 'weeklyReport', label: 'Weekly Report', description: 'Receive a weekly summary of activities' },
        ].map(({ key, label, description }) => (
          <div key={key} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <h3 className="font-medium text-gray-900">{label}</h3>
              <p className="text-sm text-gray-600">{description}</p>
            </div>
            <button
              onClick={() => handleToggle(key)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                notifications[key] ? 'bg-blue-600' : 'bg-gray-300'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  notifications[key] ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        ))}
      </div>
    </Card>
  );
}

// Security Settings
function SecuritySettings() {
  return (
    <Card>
      <h2 className="text-xl font-bold text-gray-900 mb-4">Security Settings</h2>
      <p className="text-gray-600 mb-6">Manage your account security and password.</p>

      <div className="space-y-4">
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center space-x-3">
            <Shield className="w-5 h-5 text-green-600" />
            <div>
              <p className="font-medium text-green-800">Your account is secure</p>
              <p className="text-sm text-green-600">Last password change: 30 days ago</p>
            </div>
          </div>
        </div>

        <div className="space-y-3">
          <Button variant="outline" className="w-full justify-center">
            Change Password
          </Button>
          <Button variant="outline" className="w-full justify-center">
            Enable Two-Factor Authentication
          </Button>
          <Button variant="outline" className="w-full justify-center">
            View Login History
          </Button>
        </div>
      </div>
    </Card>
  );
}

export default Settings;
