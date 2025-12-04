import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import toast from 'react-hot-toast';
import { Briefcase, Plus, Search, Edit, Trash2, Eye, Calendar, DollarSign, MapPin, X } from 'lucide-react';
import { Card, Button, Badge, LoadingSpinner, EmptyState, Modal } from '../components';
import api from '../api/config';

// Form validation schema
const jobSchema = z.object({
  title: z.string().min(3, 'Title must be at least 3 characters'),
  description: z.string().min(10, 'Description must be at least 10 characters'),
  department: z.string().min(2, 'Department is required'),
  location: z.string().min(2, 'Location is required'),
  salary_range: z.string().optional(),
  experience_required: z.string().optional(),
  required_skills: z.string().min(1, 'At least one skill is required'),
  status: z.enum(['active', 'draft', 'closed']),
});

function JobManagement() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingJob, setEditingJob] = useState(null);
  const [viewingJob, setViewingJob] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const queryClient = useQueryClient();

  const { data: jobs, isLoading, error } = useQuery({
    queryKey: ['jobs'],
    queryFn: async () => {
      const response = await api.get('/api/v1/jobs/');
      return response.data;
    },
    retry: 2,
  });

  // Filter jobs based on search and status
  const filteredJobs = jobs?.filter(job => {
    const matchesSearch = !searchQuery || 
      job.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.department?.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesStatus = filterStatus === 'all' || job.status === filterStatus;
    
    return matchesSearch && matchesStatus;
  });

  const handleCreateJob = () => {
    setEditingJob(null);
    setShowCreateForm(true);
  };

  const handleEditJob = (job) => {
    setEditingJob(job);
    setShowCreateForm(true);
  };

  const handleViewJob = (job) => {
    setViewingJob(job);
  };

  const handleCloseForm = () => {
    setShowCreateForm(false);
    setEditingJob(null);
  };

  if (isLoading) {
    return (
      <div className="p-8">
        <LoadingSpinner size="lg" text="Loading jobs..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <EmptyState
          icon={Briefcase}
          title="Failed to load jobs"
          description="Make sure the backend server is running and try again."
        />
      </div>
    );
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center">
            <Briefcase className="mr-3 text-blue-600" />
            Job Management
          </h1>
          <Button onClick={handleCreateJob} icon={Plus}>
            Create New Job
          </Button>
        </div>

        {/* Search and Filters */}
        <Card>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search jobs by title, description, or department..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
                />
              </div>
            </div>
            <div>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="draft">Draft</option>
                <option value="closed">Closed</option>
              </select>
            </div>
          </div>
        </Card>
      </div>

      {/* Jobs List */}
      {filteredJobs && filteredJobs.length > 0 ? (
        <div className="grid grid-cols-1 gap-4">
          {filteredJobs.map((job) => (
            <JobCard 
              key={job.job_id || job.id} 
              job={job}
              onEdit={() => handleEditJob(job)}
              onView={() => handleViewJob(job)}
            />
          ))}
        </div>
      ) : jobs && jobs.length > 0 ? (
        <EmptyState
          icon={Search}
          title="No jobs found"
          description="Try adjusting your search or filter criteria."
          action={{
            label: 'Clear Filters',
            onClick: () => {
              setSearchQuery('');
              setFilterStatus('all');
            }
          }}
        />
      ) : (
        <EmptyState
          icon={Briefcase}
          title="No jobs yet"
          description="Create your first job posting to start finding the perfect candidates."
          action={{
            label: 'Create Job',
            onClick: handleCreateJob
          }}
        />
      )}

      {/* Create/Edit Form Modal */}
      {showCreateForm && (
        <JobFormModal
          job={editingJob}
          onClose={handleCloseForm}
          onSuccess={() => {
            handleCloseForm();
            queryClient.invalidateQueries(['jobs']);
          }}
        />
      )}

      {/* View Job Modal */}
      {viewingJob && (
        <JobViewModal
          job={viewingJob}
          onClose={() => setViewingJob(null)}
          onEdit={() => {
            setViewingJob(null);
            handleEditJob(viewingJob);
          }}
        />
      )}
    </div>
  );
}

function JobCard({ job, onEdit, onView }) {
  const getStatusVariant = (status) => {
    if (status === 'active') return 'success';
    if (status === 'closed') return 'danger';
    return 'default';
  };

  return (
    <Card className="hover:shadow-lg transition-all">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-3">
            <h3 className="text-xl font-bold text-gray-900">{job.title || 'Untitled Job'}</h3>
            <Badge variant={getStatusVariant(job.status)}>
              {job.status || 'draft'}
            </Badge>
          </div>

          <p className="text-gray-600 mb-4 line-clamp-2">{job.description || 'No description'}</p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
            {job.department && (
              <div className="flex items-center text-sm text-gray-600">
                <Briefcase className="w-4 h-4 mr-2" />
                {job.department}
              </div>
            )}
            {job.location && (
              <div className="flex items-center text-sm text-gray-600">
                <MapPin className="w-4 h-4 mr-2" />
                {job.location}
              </div>
            )}
            {job.salary_range && (
              <div className="flex items-center text-sm text-gray-600">
                <DollarSign className="w-4 h-4 mr-2" />
                {job.salary_range}
              </div>
            )}
          </div>

          {job.required_skills && job.required_skills.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {job.required_skills.slice(0, 8).map((skill, idx) => (
                <Badge key={idx} variant="primary">{skill}</Badge>
              ))}
              {job.required_skills.length > 8 && (
                <Badge variant="default">+{job.required_skills.length - 8} more</Badge>
              )}
            </div>
          )}
        </div>

        <div className="ml-6 flex flex-col space-y-2">
          <Button variant="outline" size="sm" onClick={onView} icon={Eye}>
            View
          </Button>
          <Button variant="outline" size="sm" onClick={onEdit} icon={Edit}>
            Edit
          </Button>
        </div>
      </div>
    </Card>
  );
}

// Job Form Modal Component
function JobFormModal({ job, onClose, onSuccess }) {
  const isEditing = !!job;
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(jobSchema),
    defaultValues: job ? {
      ...job,
      required_skills: Array.isArray(job.required_skills) 
        ? job.required_skills.join(', ') 
        : job.required_skills || '',
    } : {
      status: 'draft',
    },
  });

  const createMutation = useMutation({
    mutationFn: async (data) => {
      const payload = {
        ...data,
        required_skills: data.required_skills.split(',').map(s => s.trim()).filter(Boolean),
      };
      
      if (isEditing) {
        await api.put(`/api/v1/jobs/${job.job_id || job.id}`, payload);
      } else {
        await api.post('/api/v1/jobs/', payload);
      }
    },
    onSuccess: () => {
      toast.success(isEditing ? 'Job updated successfully!' : 'Job created successfully!');
      queryClient.invalidateQueries(['jobs']);
      onSuccess();
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to save job');
    },
  });

  const onSubmit = (data) => {
    createMutation.mutate(data);
  };

  return (
    <Modal
      isOpen={true}
      onClose={onClose}
      title={isEditing ? 'Edit Job' : 'Create New Job'}
      size="lg"
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Job Title *
          </label>
          <input
            type="text"
            {...register('title')}
            className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
            placeholder="e.g., Senior Software Engineer"
          />
          {errors.title && (
            <p className="text-red-500 text-sm mt-1">{errors.title.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description *
          </label>
          <textarea
            {...register('description')}
            rows={4}
            className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
            placeholder="Describe the role and responsibilities..."
          />
          {errors.description && (
            <p className="text-red-500 text-sm mt-1">{errors.description.message}</p>
          )}
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Department *
            </label>
            <input
              type="text"
              {...register('department')}
              className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
              placeholder="e.g., Engineering"
            />
            {errors.department && (
              <p className="text-red-500 text-sm mt-1">{errors.department.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Location *
            </label>
            <input
              type="text"
              {...register('location')}
              className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
              placeholder="e.g., San Francisco, CA"
            />
            {errors.location && (
              <p className="text-red-500 text-sm mt-1">{errors.location.message}</p>
            )}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Salary Range
            </label>
            <input
              type="text"
              {...register('salary_range')}
              className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
              placeholder="e.g., $100k - $150k"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Experience Required
            </label>
            <input
              type="text"
              {...register('experience_required')}
              className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
              placeholder="e.g., 3-5 years"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Required Skills * (comma-separated)
          </label>
          <input
            type="text"
            {...register('required_skills')}
            className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
            placeholder="e.g., Python, FastAPI, React, PostgreSQL"
          />
          {errors.required_skills && (
            <p className="text-red-500 text-sm mt-1">{errors.required_skills.message}</p>
          )}
          <p className="text-sm text-gray-500 mt-1">Separate skills with commas</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Status *
          </label>
          <select
            {...register('status')}
            className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
          >
            <option value="draft">Draft</option>
            <option value="active">Active</option>
            <option value="closed">Closed</option>
          </select>
        </div>

        <div className="flex justify-end space-x-3 pt-4">
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" loading={isSubmitting}>
            {isEditing ? 'Update Job' : 'Create Job'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// Job View Modal Component
function JobViewModal({ job, onClose, onEdit }) {
  return (
    <Modal
      isOpen={true}
      onClose={onClose}
      title={job.title}
      size="lg"
    >
      <div className="space-y-6">
        <div className="flex items-center space-x-3">
          <Badge variant={job.status === 'active' ? 'success' : 'default'}>
            {job.status}
          </Badge>
          {job.department && <Badge variant="primary">{job.department}</Badge>}
        </div>

        <div>
          <h3 className="font-semibold text-gray-900 mb-2">Description</h3>
          <p className="text-gray-700">{job.description}</p>
        </div>

        <div className="grid grid-cols-2 gap-4">
          {job.location && (
            <div>
              <h4 className="font-medium text-gray-700 mb-1 flex items-center">
                <MapPin className="w-4 h-4 mr-2" />
                Location
              </h4>
              <p className="text-gray-600">{job.location}</p>
            </div>
          )}
          {job.salary_range && (
            <div>
              <h4 className="font-medium text-gray-700 mb-1 flex items-center">
                <DollarSign className="w-4 h-4 mr-2" />
                Salary Range
              </h4>
              <p className="text-gray-600">{job.salary_range}</p>
            </div>
          )}
        </div>

        {job.experience_required && (
          <div>
            <h4 className="font-medium text-gray-700 mb-1 flex items-center">
              <Calendar className="w-4 h-4 mr-2" />
              Experience Required
            </h4>
            <p className="text-gray-600">{job.experience_required}</p>
          </div>
        )}

        {job.required_skills && job.required_skills.length > 0 && (
          <div>
            <h4 className="font-medium text-gray-700 mb-2">Required Skills</h4>
            <div className="flex flex-wrap gap-2">
              {job.required_skills.map((skill, idx) => (
                <Badge key={idx} variant="primary">{skill}</Badge>
              ))}
            </div>
          </div>
        )}

        <div className="flex justify-end space-x-3 pt-4 border-t">
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
          <Button onClick={onEdit} icon={Edit}>
            Edit Job
          </Button>
        </div>
      </div>
    </Modal>
  );
}

export default JobManagement;
