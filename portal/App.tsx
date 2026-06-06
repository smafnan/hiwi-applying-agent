import React, { useState } from 'react';
import { Upload, FileText, User, Zap, BarChart3, Mail, Calendar, BookOpen, Trophy } from 'lucide-react';

interface UserProfile {
  name: string;
  email: string;
  degree: string;
  degreeStatus: string;
  topSkills: string[];
  strongestProjects: string[];
  keyAchievement: string;
  workExperience: { role: string; company: string; duration: string }[];
}

interface ApplicationStatus {
  userId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  professorsFound: number;
  emailsDrafted: number;
  progress: number;
  createdAt: string;
}

export default function App() {
  const [currentStep, setCurrentStep] = useState<'intro' | 'profile' | 'upload' | 'preview' | 'results'>('intro');
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [applicationStatus, setApplicationStatus] = useState<ApplicationStatus | null>(null);
  const [uploadedFiles, setUploadedFiles] = useState<{ transcript?: File; resume?: File; coverLetter?: File }>({});

  const steps = [
    { id: 'intro', label: 'Welcome', icon: '🎓' },
    { id: 'profile', label: 'Your Profile', icon: '👤' },
    { id: 'upload', label: 'Upload Files', icon: '📄' },
    { id: 'preview', label: 'Review', icon: '👀' },
    { id: 'results', label: 'Results', icon: '🎉' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Zap className="w-8 h-8 text-indigo-600" />
              <h1 className="text-2xl font-bold text-gray-900">HiWi Applying Agent</h1>
            </div>
            <p className="text-gray-600">Find your perfect HiWi position at BTU</p>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-12">
        {/* Progress Steps */}
        <div className="mb-12">
          <div className="flex justify-between items-center">
            {steps.map((step, index) => (
              <React.Fragment key={step.id}>
                <div
                  onClick={() => setCurrentStep(step.id as any)}
                  className={`flex flex-col items-center cursor-pointer transition-all ${
                    currentStep === step.id ? 'opacity-100' : 'opacity-60 hover:opacity-80'
                  }`}
                >
                  <div
                    className={`w-12 h-12 rounded-full flex items-center justify-center text-xl mb-2 transition-all ${
                      currentStep === step.id
                        ? 'bg-indigo-600 text-white shadow-lg scale-110'
                        : 'bg-white border-2 border-gray-300 text-gray-600'
                    }`}
                  >
                    {step.icon}
                  </div>
                  <span className="text-sm font-medium text-gray-700">{step.label}</span>
                </div>
                {index < steps.length - 1 && (
                  <div className="flex-1 h-1 mx-4 bg-gray-200 mt-6"></div>
                )}
              </React.Fragment>
            ))}
          </div>
        </div>

        {/* Content Sections */}
        {currentStep === 'intro' && <IntroSection onNext={() => setCurrentStep('profile')} />}
        {currentStep === 'profile' && <ProfileSection onNext={() => setCurrentStep('upload')} onProfileChange={setProfile} />}
        {currentStep === 'upload' && <UploadSection onNext={() => setCurrentStep('preview')} onFilesChange={setUploadedFiles} />}
        {currentStep === 'preview' && <PreviewSection profile={profile} files={uploadedFiles} onSubmit={() => setCurrentStep('results')} />}
        {currentStep === 'results' && <ResultsSection />}
      </main>
    </div>
  );
}

// ============ Components ============

function IntroSection({ onNext }: { onNext: () => void }) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-12">
      <div className="max-w-3xl mx-auto text-center">
        <h2 className="text-4xl font-bold text-gray-900 mb-6">Welcome to HiWi Applying Agent</h2>
        <p className="text-xl text-gray-600 mb-8">
          Tired of manually searching for HiWi positions? We automate the entire process:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 my-12">
          <div className="p-6 bg-blue-50 rounded-lg border border-blue-200">
            <Upload className="w-8 h-8 text-blue-600 mx-auto mb-4" />
            <h3 className="font-semibold text-gray-900 mb-2">Upload Your Info</h3>
            <p className="text-sm text-gray-600">Share your transcript, resume, and profile</p>
          </div>

          <div className="p-6 bg-purple-50 rounded-lg border border-purple-200">
            <Mail className="w-8 h-8 text-purple-600 mx-auto mb-4" />
            <h3 className="font-semibold text-gray-900 mb-2">Auto-Generate Emails</h3>
            <p className="text-sm text-gray-600">Personalized emails to 20+ professors</p>
          </div>

          <div className="p-6 bg-green-50 rounded-lg border border-green-200">
            <Trophy className="w-8 h-8 text-green-600 mx-auto mb-4" />
            <h3 className="font-semibold text-gray-900 mb-2">Land Your Position</h3>
            <p className="text-sm text-gray-600">Ready-to-send emails ranked by fit</p>
          </div>
        </div>

        <div className="bg-indigo-50 border-l-4 border-indigo-600 p-6 mb-8">
          <p className="text-indigo-900">
            <strong>⏱️ Takes 3 minutes to set up</strong> • <strong>45 minutes to process</strong> • <strong>Results ready instantly</strong>
          </p>
        </div>

        <button
          onClick={onNext}
          className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-8 rounded-lg transition-colors"
        >
          Get Started →
        </button>
      </div>
    </div>
  );
}

function ProfileSection({ onNext, onProfileChange }: { onNext: () => void; onProfileChange: (p: UserProfile) => void }) {
  const [profile, setProfile] = useState<UserProfile>({
    name: '',
    email: '',
    degree: 'M.Sc.',
    degreeStatus: 'ongoing',
    topSkills: ['', '', '', ''],
    strongestProjects: ['', ''],
    keyAchievement: '',
    workExperience: [{ role: '', company: '', duration: '' }]
  });

  const handleChange = (field: string, value: any) => {
    const updated = { ...profile, [field]: value };
    setProfile(updated);
    onProfileChange(updated);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <h2 className="text-3xl font-bold text-gray-900 mb-8">Your Profile</h2>

      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
            <input
              type="text"
              value={profile.name}
              onChange={(e) => handleChange('name', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Jane Müller"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
            <input
              type="email"
              value={profile.email}
              onChange={(e) => handleChange('email', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="jane@example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Degree</label>
            <input
              type="text"
              value={profile.degree}
              onChange={(e) => handleChange('degree', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="M.Sc. Computer Science"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select
              value={profile.degreeStatus}
              onChange={(e) => handleChange('degreeStatus', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option>ongoing</option>
              <option>completed</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Top Skills (comma-separated or enter one per field)
          </label>
          <div className="grid grid-cols-2 gap-2">
            {profile.topSkills.map((skill, i) => (
              <input
                key={i}
                type="text"
                value={skill}
                onChange={(e) => {
                  const updated = [...profile.topSkills];
                  updated[i] = e.target.value;
                  handleChange('topSkills', updated);
                }}
                placeholder={`Skill ${i + 1}`}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Key Achievement</label>
          <textarea
            value={profile.keyAchievement}
            onChange={(e) => handleChange('keyAchievement', e.target.value)}
            rows={3}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            placeholder="E.g., Built ML system improving user engagement by 40%"
          />
        </div>

        <button
          onClick={onNext}
          className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 rounded-lg transition-colors"
        >
          Continue to Upload →
        </button>
      </div>
    </div>
  );
}

function UploadSection({ onNext, onFilesChange }: { onNext: () => void; onFilesChange: (f: any) => void }) {
  const [files, setFiles] = useState<any>({});

  const handleFileChange = (type: string, file: File | null) => {
    const updated = { ...files, [type]: file };
    setFiles(updated);
    onFilesChange(updated);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <h2 className="text-3xl font-bold text-gray-900 mb-8">Upload Your Files</h2>

      <div className="space-y-8">
        <FileUploadBox
          title="BTU Transcript (Notenübersicht)"
          description="Your grade transcript PDF from BTU"
          icon={<FileText className="w-12 h-12 text-blue-600" />}
          required
          onFileSelect={(file) => handleFileChange('transcript', file)}
        />

        <FileUploadBox
          title="Resume/CV"
          description="Your CV or resume (optional but recommended)"
          icon={<FileText className="w-12 h-12 text-green-600" />}
          onFileSelect={(file) => handleFileChange('resume', file)}
        />

        <FileUploadBox
          title="Cover Letter"
          description="Any existing cover letter (optional)"
          icon={<FileText className="w-12 h-12 text-purple-600" />}
          onFileSelect={(file) => handleFileChange('coverLetter', file)}
        />

        <button
          onClick={onNext}
          className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 rounded-lg transition-colors"
        >
          Review Everything →
        </button>
      </div>
    </div>
  );
}

function FileUploadBox({
  title,
  description,
  icon,
  required = false,
  onFileSelect
}: {
  title: string;
  description: string;
  icon: React.ReactNode;
  required?: boolean;
  onFileSelect: (file: File | null) => void;
}) {
  const [isDragActive, setIsDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleDrag = (e: any) => {
    e.preventDefault();
    setIsDragActive(e.type === 'dragenter' || e.type === 'dragover');
  };

  const handleDrop = (e: any) => {
    e.preventDefault();
    setIsDragActive(false);
    const file = e.dataTransfer.files?.[0];
    if (file) {
      setSelectedFile(file);
      onFileSelect(file);
    }
  };

  return (
    <div
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      className={`border-2 border-dashed rounded-lg p-8 transition-colors ${
        isDragActive ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300 hover:border-gray-400'
      }`}
    >
      <div className="flex flex-col items-center">
        {icon}
        <h3 className="mt-4 text-lg font-semibold text-gray-900">{title}</h3>
        <p className="text-sm text-gray-600 mt-1">{description}</p>
        {required && <span className="text-red-600 text-sm font-medium mt-2">*Required</span>}

        <label className="mt-4 cursor-pointer">
          <input
            type="file"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) {
                setSelectedFile(file);
                onFileSelect(file);
              }
            }}
            className="hidden"
            accept=".pdf,.doc,.docx"
          />
          <span className="bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded-lg inline-block">
            Browse Files
          </span>
        </label>

        {selectedFile && <p className="text-green-600 text-sm mt-3">✓ {selectedFile.name}</p>}
      </div>
    </div>
  );
}

function PreviewSection({
  profile,
  files,
  onSubmit
}: {
  profile: UserProfile | null;
  files: any;
  onSubmit: () => void;
}) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <h2 className="text-3xl font-bold text-gray-900 mb-8">Review Your Information</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Profile Summary</h3>
          <div className="space-y-3 text-gray-700">
            <p><strong>Name:</strong> {profile?.name}</p>
            <p><strong>Email:</strong> {profile?.email}</p>
            <p><strong>Degree:</strong> {profile?.degree} ({profile?.degreeStatus})</p>
            <p><strong>Skills:</strong> {profile?.topSkills.filter(s => s).join(', ')}</p>
          </div>
        </div>

        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Uploaded Files</h3>
          <div className="space-y-2">
            {files.transcript && <p className="text-green-600">✓ Transcript uploaded</p>}
            {files.resume && <p className="text-green-600">✓ Resume uploaded</p>}
            {files.coverLetter && <p className="text-green-600">✓ Cover letter uploaded</p>}
            {!files.transcript && <p className="text-red-600">✗ Transcript required</p>}
          </div>
        </div>
      </div>

      <button
        onClick={onSubmit}
        className="w-full mt-8 bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 rounded-lg transition-colors"
      >
        Start Processing 🚀
      </button>
    </div>
  );
}

function ResultsSection() {
  const [progress, setProgress] = React.useState(0);

  React.useEffect(() => {
    const interval = setInterval(() => {
      setProgress((p) => (p < 100 ? p + Math.random() * 30 : 100));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <h2 className="text-3xl font-bold text-gray-900 mb-8">Processing Your Application</h2>

      <div className="space-y-8">
        <div>
          <div className="flex justify-between mb-2">
            <span className="text-gray-700 font-medium">Pipeline Progress</span>
            <span className="text-indigo-600 font-bold">{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
            <div
              className="bg-gradient-to-r from-indigo-600 to-purple-600 h-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 bg-blue-50 rounded-lg border border-blue-200">
            <Zap className="w-8 h-8 text-blue-600 mb-2" />
            <p className="text-2xl font-bold text-gray-900">23</p>
            <p className="text-sm text-gray-600">Professors Found</p>
          </div>

          <div className="p-6 bg-purple-50 rounded-lg border border-purple-200">
            <Mail className="w-8 h-8 text-purple-600 mb-2" />
            <p className="text-2xl font-bold text-gray-900">23</p>
            <p className="text-sm text-gray-600">Personalized Emails</p>
          </div>

          <div className="p-6 bg-green-50 rounded-lg border border-green-200">
            <BarChart3 className="w-8 h-8 text-green-600 mb-2" />
            <p className="text-2xl font-bold text-gray-900">15</p>
            <p className="text-sm text-gray-600">High-Fit Targets</p>
          </div>
        </div>

        {progress === 100 && (
          <div className="bg-green-50 border-l-4 border-green-600 p-6">
            <p className="text-green-900 font-semibold mb-4">✅ Processing Complete!</p>
            <p className="text-green-800 mb-4">Your email tracker is ready. Download it and start sending!</p>
            <button className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-6 rounded-lg transition-colors">
              Download Excel File ⬇️
            </button>
          </div>
        )}

        <div className="bg-gray-50 p-6 rounded-lg">
          <h3 className="font-semibold text-gray-900 mb-4">What's Next?</h3>
          <ol className="space-y-2 text-gray-700">
            <li>1. Download your <strong>outreach_tracker.xlsx</strong></li>
            <li>2. Sort by <strong>Score</strong> (highest fit first)</li>
            <li>3. Send <strong>5-10 emails/day</strong> to avoid spam filters</li>
            <li>4. Use <strong>Day 7 and Day 18</strong> follow-up templates</li>
            <li>5. Track responses in the <strong>Notes</strong> column</li>
          </ol>
        </div>
      </div>
    </div>
  );
}
