import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import toast from 'react-hot-toast';
import { Calendar, Clock, Users, Video, Plus, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { Card, Button, Badge, LoadingSpinner, EmptyState, Modal } from '../components';
import api from '../api/config';

const interviewSchema = z.object({
  candidate_name: z.string().min(2, 'Candidate name is required'),
  position: z.string().min(2, 'Position is required'),
  interview_date: z.string().min(1, 'Date is required'),
  interview_time: z.string().min(1, 'Time is required'),
  interviewer: z.string().min(2, 'Interviewer name is required'),
  meeting_link: z.string().url('Invalid URL').optional().or(z.literal('')),
  notes: z.string().optional(),
});

function InterviewManagement() {
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [selectedInterview, setSelectedInterview] = useState(null);
  const [filterStatus, setFilterStatus] = useState('all');
  const queryClient = useQueryClient();

  // Mock data since we don't have an interviews endpoint
  const mockInterviews = [
    {
      id: 1,
      candidate_name: 'John Doe',
      position: 'Senior Software Engineer',
      interview_date: '2025-11-25',
      interview_time: '10:00',
      interviewer: 'Jane Smith',
      status: 'scheduled',
      meeting_link: 'https://zoom.us/j/123456789',
      notes: 'Technical interview - focus on system design'
    },
    {
      id: 2,
      candidate_name: 'Alice Johnson',
      position: 'Product Manager',
      interview_date: '2025-11-26',
      interview_time: '14:00',
      interviewer: 'Bob Wilson',
      status: 'completed',
      notes: 'Great communication skills'
    },
    {
      id: 3,
      candidate_name: 'Mike Chen',
      position: 'Data Scientist',
      interview_date: '2025-11-24',
      interview_time: '15:30',
      interviewer: 'Sarah Lee',
      status: 'cancelled',
      notes: 'Candidate withdrew'
    },
  ];

  const interviews = mockInterviews;
  const isLoading = false;

  const filteredInterviews = interviews?.filter(interview => {
    if (filterStatus === 'all') return true;
    return interview.status === filterStatus;
  });

  const getStatusIcon = (status) => {
    if (status === 'scheduled') return <Clock className="w-5 h-5 text-blue-600" />;
    if (status === 'completed') return <CheckCircle className="w-5 h-5 text-green-600" />;
    return <XCircle className="w-5 h-5 text-red-600" />;
  };

  const getStatusVariant = (status) => {
    if (status === 'scheduled') return 'primary';
    if (status === 'completed') return 'success';
    return 'danger';
  };

  if (isLoading) {
    return (
      <div className="p-8">
        <LoadingSpinner size="lg" text="Loading interviews..." />
      </div>
    );
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center">
            <Calendar className="mr-3 text-blue-600" />
            Interview Management
          </h1>
          <Button onClick={() => setShowScheduleModal(true)} icon={Plus}>
            Schedule Interview
          </Button>
        </div>

        {/* Filters */}
        <Card>
          <div className="flex items-center space-x-4">
            <span className="text-sm font-medium text-gray-700">Filter by Status:</span>
            <div className="flex space-x-2">
              {['all', 'scheduled', 'completed', 'cancelled'].map(status => (
                <Button
                  key={status}
                  variant={filterStatus === status ? 'primary' : 'outline'}
                  size="sm"
                  onClick={() => setFilterStatus(status)}
                >
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </Button>
              ))}
            </div>
          </div>
        </Card>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">Total Interviews</p>
            <p className="text-3xl font-bold text-gray-900">{interviews.length}</p>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">Scheduled</p>
            <p className="text-3xl font-bold text-blue-600">
              {interviews.filter(i => i.status === 'scheduled').length}
            </p>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">Completed</p>
            <p className="text-3xl font-bold text-green-600">
              {interviews.filter(i => i.status === 'completed').length}
            </p>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">Cancelled</p>
            <p className="text-3xl font-bold text-red-600">
              {interviews.filter(i => i.status === 'cancelled').length}
            </p>
          </div>
        </Card>
      </div>

      {/* Interviews List */}
      {filteredInterviews && filteredInterviews.length > 0 ? (
        <div className="grid grid-cols-1 gap-4">
          {filteredInterviews.map((interview) => (
            <Card key={interview.id} className="hover:shadow-lg transition-all">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4 flex-1">
                  <div className="mt-1">
                    {getStatusIcon(interview.status)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-xl font-bold text-gray-900">{interview.candidate_name}</h3>
                      <Badge variant={getStatusVariant(interview.status)}>
                        {interview.status}
                      </Badge>
                    </div>
                    <p className="text-gray-600 mb-3">{interview.position}</p>
                    
                    <div className="grid grid-cols-2 gap-3 mb-3">
                      <div className="flex items-center text-sm text-gray-600">
                        <Calendar className="w-4 h-4 mr-2" />
                        {new Date(interview.interview_date).toLocaleDateString('en-US', {
                          weekday: 'short',
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric'
                        })}
                      </div>
                      <div className="flex items-center text-sm text-gray-600">
                        <Clock className="w-4 h-4 mr-2" />
                        {interview.interview_time}
                      </div>
                      <div className="flex items-center text-sm text-gray-600">
                        <Users className="w-4 h-4 mr-2" />
                        {interview.interviewer}
                      </div>
                      {interview.meeting_link && (
                        <div className="flex items-center text-sm text-gray-600">
                          <Video className="w-4 h-4 mr-2" />
                          <a
                            href={interview.meeting_link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:underline"
                          >
                            Join Meeting
                          </a>
                        </div>
                      )}
                    </div>

                    {interview.notes && (
                      <div className="bg-gray-50 rounded p-3">
                        <p className="text-sm text-gray-700">{interview.notes}</p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex flex-col space-y-2 ml-4">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setSelectedInterview(interview)}
                  >
                    View Details
                  </Button>
                  {interview.status === 'scheduled' && (
                    <Button variant="outline" size="sm">
                      Reschedule
                    </Button>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={Calendar}
          title="No interviews found"
          description={filterStatus === 'all' 
            ? "Schedule your first interview to get started."
            : `No ${filterStatus} interviews found.`}
          action={{
            label: 'Schedule Interview',
            onClick: () => setShowScheduleModal(true)
          }}
        />
      )}

      {/* Schedule Interview Modal */}
      {showScheduleModal && (
        <ScheduleInterviewModal
          onClose={() => setShowScheduleModal(false)}
          onSuccess={() => {
            setShowScheduleModal(false);
            toast.success('Interview scheduled successfully!');
          }}
        />
      )}

      {/* View Interview Details Modal */}
      {selectedInterview && (
        <InterviewDetailsModal
          interview={selectedInterview}
          onClose={() => setSelectedInterview(null)}
        />
      )}
    </div>
  );
}

// Schedule Interview Modal
function ScheduleInterviewModal({ onClose, onSuccess }) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(interviewSchema),
  });

  const onSubmit = async (data) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    onSuccess();
  };

  return (
    <Modal isOpen={true} onClose={onClose} title="Schedule Interview" size="lg">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Candidate Name *
            </label>
            <input
              {...register('candidate_name')}
              className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
              placeholder="John Doe"
            />
            {errors.candidate_name && (
              <p className="text-red-500 text-sm mt-1">{errors.candidate_name.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Position *
            </label>
            <input
              {...register('position')}
              className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
              placeholder="Software Engineer"
            />
            {errors.position && (
              <p className="text-red-500 text-sm mt-1">{errors.position.message}</p>
            )}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Date *
            </label>
            <input
              type="date"
              {...register('interview_date')}
              className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
            />
            {errors.interview_date && (
              <p className="text-red-500 text-sm mt-1">{errors.interview_date.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Time *
            </label>
            <input
              type="time"
              {...register('interview_time')}
              className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
            />
            {errors.interview_time && (
              <p className="text-red-500 text-sm mt-1">{errors.interview_time.message}</p>
            )}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Interviewer *
          </label>
          <input
            {...register('interviewer')}
            className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
            placeholder="Interviewer name"
          />
          {errors.interviewer && (
            <p className="text-red-500 text-sm mt-1">{errors.interviewer.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Meeting Link (optional)
          </label>
          <input
            {...register('meeting_link')}
            className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
            placeholder="https://zoom.us/j/..."
          />
          {errors.meeting_link && (
            <p className="text-red-500 text-sm mt-1">{errors.meeting_link.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Notes
          </label>
          <textarea
            {...register('notes')}
            rows={3}
            className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
            placeholder="Additional notes about the interview..."
          />
        </div>

        <div className="flex justify-end space-x-3 pt-4">
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" loading={isSubmitting}>
            Schedule Interview
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// Interview Details Modal
function InterviewDetailsModal({ interview, onClose }) {
  return (
    <Modal isOpen={true} onClose={onClose} title="Interview Details" size="lg">
      <div className="space-y-4">
        <div>
          <h3 className="font-semibold text-gray-900 mb-2">Candidate</h3>
          <p className="text-gray-700">{interview.candidate_name}</p>
        </div>

        <div>
          <h3 className="font-semibold text-gray-900 mb-2">Position</h3>
          <p className="text-gray-700">{interview.position}</p>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Date</h3>
            <p className="text-gray-700">
              {new Date(interview.interview_date).toLocaleDateString()}
            </p>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Time</h3>
            <p className="text-gray-700">{interview.interview_time}</p>
          </div>
        </div>

        <div>
          <h3 className="font-semibold text-gray-900 mb-2">Interviewer</h3>
          <p className="text-gray-700">{interview.interviewer}</p>
        </div>

        <div>
          <h3 className="font-semibold text-gray-900 mb-2">Status</h3>
          <Badge variant={interview.status === 'scheduled' ? 'primary' : interview.status === 'completed' ? 'success' : 'danger'}>
            {interview.status}
          </Badge>
        </div>

        {interview.meeting_link && (
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Meeting Link</h3>
            <a
              href={interview.meeting_link}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              {interview.meeting_link}
            </a>
          </div>
        )}

        {interview.notes && (
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Notes</h3>
            <p className="text-gray-700">{interview.notes}</p>
          </div>
        )}

        <div className="flex justify-end pt-4 border-t">
          <Button onClick={onClose}>Close</Button>
        </div>
      </div>
    </Modal>
  );
}

export default InterviewManagement;
