import React, { useState, useEffect, useRef, useCallback } from "react";
import "@/App.css";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
import {
  ShieldCheck,
  Plane,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  CreditCard,
  Workflow,
  Cloud,
  RotateCcw,
  Circle,
  Mail,
  Search,
  Zap
} from "lucide-react";
import { Button } from "./components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./components/ui/card";
import { Badge } from "./components/ui/badge";
import { ScrollArea } from "./components/ui/scroll-area";
import { Separator } from "./components/ui/separator";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Income Insurance Logo Component
const IncomeLogo = () => (
  <div className="flex items-center gap-3">
    <img
      src="https://customer-assets.emergentagent.com/job_ccdf1cdf-6e7b-4b09-8b4b-d954c003297d/artifacts/50rt4irs_image.png"
      alt="Income Insurance Logo"
      className="h-10 object-contain"
    />
  </div>
);

// Policy Holder Component
const PolicyHolderCard = ({ holder }) => (
  <Card className="border border-slate-200 shadow-sm bg-white" data-testid="policy-holder-card">
    <CardHeader className="pb-2 pt-4 px-4">
      <CardTitle className="text-xs font-bold text-black uppercase tracking-wider">
        Policy Holder
      </CardTitle>
    </CardHeader>
    <CardContent className="pt-2 px-4 pb-4">
      <div className="flex items-center gap-3">
        <div className="w-11 h-11 rounded-full bg-[#FF7600] flex items-center justify-center text-white font-bold text-base shadow-sm">
          {holder?.name?.split(' ').map(n => n[0]).join('') || 'JC'}
        </div>
        <div>
          <p className="font-bold text-black text-sm" data-testid="holder-name">{holder?.name || 'Jolene Chua'}</p>
          <p className="text-xs text-black">{holder?.membership_type || 'Premium Member'}</p>
        </div>
      </div>
    </CardContent>
  </Card>
);

// Policy Details Component
const PolicyDetailsCard = ({ policy }) => (
  <Card className="border border-slate-200 shadow-sm bg-white" data-testid="policy-details-card">
    <CardHeader className="pb-2 pt-4 px-4">
      <CardTitle className="text-xs font-bold text-black uppercase tracking-wider">
        Policy Details
      </CardTitle>
    </CardHeader>
    <CardContent className="pt-2 px-4 pb-4 space-y-3">
      <div>
        <p className="text-xs font-bold text-black">Policy Number</p>
        <p className="font-mono text-sm font-semibold text-black" data-testid="policy-number">{policy?.policy_number || 'TRV-2026-0014879'}</p>
      </div>
      <div>
        <p className="text-xs font-bold text-black">Coverage</p>
        <p className="text-sm text-black">{policy?.policy_type || 'Comprehensive Travel Insurance'}</p>
      </div>
      <div>
        <p className="text-xs font-bold text-black">Flight Delay Coverage</p>
        <p className="text-sm font-semibold text-emerald-600" data-testid="delay-coverage">{policy?.flight_delay_coverage || '$100 per 6 hours'}</p>
      </div>
      <div>
        <p className="text-xs font-bold text-black">Status</p>
        <Badge className="bg-emerald-100 text-emerald-700 hover:bg-emerald-100 mt-1 text-xs font-bold" data-testid="policy-status">
          Active
        </Badge>
      </div>
    </CardContent>
  </Card>
);

// Flight Information Component
const FlightInfoCard = ({ flights }) => {
  const delayedFlight = flights?.find(f => f.status === 'Delayed');

  return (
    <Card className="border border-slate-200 shadow-sm bg-white" data-testid="flight-info-card">
      <CardHeader className="pb-2 pt-4 px-4">
        <CardTitle className="text-xs font-bold text-black uppercase tracking-wider flex items-center gap-2">
          <Plane className="w-3.5 h-3.5" />
          Flight Information
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-2 px-4 pb-4 space-y-4">
        {/* Flight Route Visualization */}
        <div className="flex items-center justify-between py-3 relative">
          <div className="absolute left-6 right-6 top-1/2 h-0.5 bg-slate-200 -translate-y-1/2 z-0">
            <div className="absolute left-0 w-1/2 h-full bg-[#FF7600]"></div>
          </div>
          {['SIN', 'HAK', 'NRT'].map((code, idx) => (
            <div key={code} className="flex flex-col items-center z-10">
              <div className={`w-3 h-3 rounded-full ${idx === 1 ? 'bg-amber-500' : idx === 0 ? 'bg-[#FF7600]' : 'bg-slate-300'} ring-2 ring-white`}></div>
              <span className="text-xs font-mono font-bold mt-1.5 text-black">{code}</span>
            </div>
          ))}
        </div>

        {delayedFlight && (
          <>
            <Separator className="bg-slate-100" />
            <div className="space-y-3">
              <div>
                <p className="text-xs font-bold text-black">Flight</p>
                <p className="font-mono text-sm font-semibold text-black" data-testid="flight-number">{delayedFlight.flight_number}</p>
              </div>
              <div>
                <p className="text-xs font-bold text-black">Airline</p>
                <p className="text-sm text-black">{delayedFlight.airline}</p>
              </div>
              <div>
                <p className="text-xs font-bold text-black">Status</p>
                <Badge className="bg-amber-100 text-amber-700 hover:bg-amber-100 mt-1 flex items-center gap-1 w-fit text-xs font-bold" data-testid="flight-status">
                  <AlertTriangle className="w-3 h-3" />
                  Delayed {delayedFlight.delay_hours}h
                </Badge>
              </div>
              <div>
                <p className="text-xs font-bold text-black">Date & Time</p>
                <p className="text-sm text-black">{delayedFlight.scheduled_departure}</p>
              </div>
              <div>
                <p className="text-xs font-bold text-black">Delay Reason</p>
                <p className="text-xs text-amber-600 font-semibold flex items-center gap-1 mt-0.5">
                  <Cloud className="w-3 h-3" />
                  {delayedFlight.delay_reason}
                </p>
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
};

// Agent Card Component
const AgentCard = ({ title, subtitle, icon: Icon, active, completed, showSpinner }) => (
  <motion.div
    layout
    className={`bg-white rounded-xl border-2 p-5 transition-all duration-300 ${
      active ? 'border-[#FF7600] shadow-lg shadow-orange-100' : 'border-slate-200'
    }`}
    data-testid={`agent-card-${title.toLowerCase().replace(/\s+/g, '-')}`}
  >
    <div className="flex items-start justify-between">
      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
          active ? 'bg-emerald-100 text-emerald-600' : 'bg-slate-100 text-black'
        }`}>
          <Icon className="w-5 h-5" />
        </div>
        <div>
          <h3 className="font-bold text-black text-sm">{title}</h3>
          <p className="text-xs text-black">{subtitle}</p>
        </div>
      </div>
      {showSpinner && (
        <Loader2 className="w-5 h-5 text-emerald-500 animate-spin" />
      )}
      {completed && !showSpinner && (
        <CheckCircle2 className="w-5 h-5 text-emerald-500" />
      )}
    </div>
  </motion.div>
);

// Validation Progress Component - Separate Card
const ValidationProgressCard = ({ steps, visible }) => {
  if (!visible) return null;

  return (
    <Card className="border-2 border-slate-200 shadow-sm bg-white" data-testid="validation-progress">
      <CardHeader className="pb-2 pt-4 px-5">
        <CardTitle className="text-xs font-bold text-black uppercase tracking-wider">
          Validation Progress
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-2 px-5 pb-4">
        <div className="space-y-2">
          {steps?.map((step, idx) => (
            <motion.div
              key={step.step_number}
              className={`flex items-center gap-3 py-1.5 ${
                step.status === 'pending' ? 'opacity-60' : ''
              }`}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: step.status === 'pending' ? 0.6 : 1, x: 0 }}
              transition={{ delay: idx * 0.05 }}
              data-testid={`validation-step-${step.step_number}`}
            >
              <div className="flex-shrink-0">
                {step.status === 'completed' ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                ) : step.status === 'in_progress' ? (
                  <div className="relative">
                    <Circle className="w-4 h-4 text-slate-200" />
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="w-2 h-2 bg-[#FF7600] rounded-full animate-pulse"></div>
                    </div>
                  </div>
                ) : (
                  <Circle className="w-4 h-4 text-slate-300" />
                )}
              </div>
              <span className={`text-sm flex-1 ${
                step.status === 'completed' ? 'text-black font-semibold' :
                step.status === 'in_progress' ? 'text-[#FF7600] font-semibold' :
                'text-black'
              }`}>
                {step.step_number}. {step.name}
              </span>
              {step.status === 'completed' && (
                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              )}
            </motion.div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

// Terminal Log Component - White Background with Orange Border
const TerminalLog = ({ logs }) => {
  const scrollRef = useRef(null);

  // Auto-scroll to bottom when new logs arrive (like real chat)
  useEffect(() => {
    if (scrollRef.current) {
      const scrollContainer = scrollRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  }, [logs]);

  const getLogIcon = (type, message) => {
    if (type === 'success') return <CheckCircle2 className="w-3 h-3 text-green-600 flex-shrink-0" />;
    if (type === 'api_call') return <Zap className="w-3 h-3 text-blue-600 flex-shrink-0" />;
    if (message.includes('Processing')) return <Search className="w-3 h-3 text-black flex-shrink-0" />;
    return null;
  };

  return (
    <div className="h-full flex flex-col bg-white rounded-xl overflow-hidden shadow-xl border-2 border-[#FF7600]" data-testid="terminal-log">
      <div className="px-4 py-3 border-b-2 border-[#FF7600] flex items-center gap-3 bg-[#FF7600]">
        <div className="flex gap-1.5">
          <div className="w-3 h-3 rounded-full bg-white/30"></div>
          <div className="w-3 h-3 rounded-full bg-white/50"></div>
          <div className="w-3 h-3 rounded-full bg-white/70"></div>
        </div>
        <span className="text-white text-xs font-bold uppercase tracking-wider">Agent Activity Log</span>
      </div>
      <ScrollArea className="flex-1 p-4" ref={scrollRef}>
        <div className="space-y-3 text-sm flex flex-col">
          {logs?.length === 0 && (
            <div className="text-black">
              Waiting for agent activity...
            </div>
          )}
          <AnimatePresence>
            {logs?.map((log, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="log-entry"
                data-testid={`log-entry-${idx}`}
              >
                <div className="flex items-start gap-2">
                  <span className="text-black font-bold flex-shrink-0">{log.agent}:</span>
                </div>
                <div className="ml-4 mt-1 flex items-start gap-2 text-black">
                  {getLogIcon(log.log_type, log.message)}
                  <span className={log.log_type === 'success' ? 'font-semibold' : ''}>
                    {log.message}
                  </span>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </ScrollArea>
    </div>
  );
};

// Claim Summary Component
const ClaimSummary = ({ claim, visible }) => {
  if (!visible || !claim) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-emerald-50 border-2 border-emerald-200 rounded-xl p-5 mt-4"
      data-testid="claim-summary"
    >
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center">
          <CheckCircle2 className="w-5 h-5 text-emerald-600" />
        </div>
        <div>
          <h3 className="font-bold text-black text-sm">Claim Approved & Paid</h3>
          <p className="text-xs text-black">Auto-processed by AI Agents</p>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <p className="text-black font-bold text-xs">Claim Number</p>
          <p className="font-mono font-semibold text-black">{claim.claim_id}</p>
        </div>
        <div>
          <p className="text-black font-bold text-xs">Claim Payment amount</p>
          <p className="font-bold text-black text-lg">${claim.compensation_amount}</p>
        </div>
      </div>
    </motion.div>
  );
};

// Main App Component
function App() {
  const [scenario, setScenario] = useState(null);
  const [claimId, setClaimId] = useState(null);
  const [workflowStatus, setWorkflowStatus] = useState('idle'); // idle, running, completed
  const [currentStep, setCurrentStep] = useState(0);
  const [validationSteps, setValidationSteps] = useState([]);
  const [logs, setLogs] = useState([]);
  const [activeAgent, setActiveAgent] = useState(null);
  const [claimDetails, setClaimDetails] = useState(null);

  // Fetch scenario on load and auto-start workflow
  useEffect(() => {
    const initializeApp = async () => {
      await fetchScenario();
      // Auto-start workflow after scenario is loaded
      setTimeout(() => {
        startWorkflow();
      }, 500);
    };
    initializeApp();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchScenario = async () => {
    try {
      const response = await axios.get(`${API}/scenario`);
      setScenario(response.data);
      setValidationSteps(response.data.validation_steps);
    } catch (e) {
      console.error("Error fetching scenario:", e);
    }
  };

  const addLog = (timestamp, agent, message, logType = 'info') => {
    setLogs(prev => [...prev, { timestamp, agent, message, log_type: logType }]);
  };

  const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

  const startWorkflow = useCallback(async () => {
    setWorkflowStatus('running');
    setLogs([]);
    setCurrentStep(0);
    setClaimDetails(null);

    const now = new Date();
    const timestamp = now.toLocaleTimeString('en-GB', { hour12: false });

    // Start claim
    try {
      const startResponse = await axios.post(`${API}/claim/start`);
      const newClaimId = startResponse.data.id;
      setClaimId(newClaimId);

      // Orchestrator starts
      setActiveAgent('orchestrator');
      addLog(timestamp, 'Orchestrator Agent', 'Initiating automated claim workflow...', 'info');
      await delay(2000);
      addLog(timestamp, 'Orchestrator Agent', 'Flight delay detected: SQ656 (SIN → HAK)', 'warning');
      await delay(2000);
      addLog(timestamp, 'Orchestrator Agent', 'Handing off to Claim Processing Agent for detailed validation...', 'success');
      await delay(30000); // 30 second delay

      // Claim Processing Agent
      setActiveAgent('claim');

      // Process each validation step
      for (let step = 1; step <= 6; step++) {
        const stepTimestamp = new Date().toLocaleTimeString('en-GB', { hour12: false });

        // Update step to in_progress
        setValidationSteps(prev => prev.map(s =>
          s.step_number === step ? { ...s, status: 'in_progress' } : s
        ));
        setCurrentStep(step);

        // Call API to process step
        try {
          const stepResponse = await axios.post(`${API}/claim/${newClaimId}/process-step?step_number=${step}`);

          // Add logs from response
          stepResponse.data.logs.forEach(log => {
            addLog(log.timestamp, log.agent, log.message, log.log_type);
          });

          // Update step to completed
          setValidationSteps(prev => prev.map(s =>
            s.step_number === step ? {
              ...s,
              status: 'completed',
              details: stepResponse.data.result?.details
            } : s
          ));

          // Get claim details if step 5
          if (step === 5 && stepResponse.data.result?.compensation) {
            // Fetch updated claim to get claim details
            const claimResponse = await axios.get(`${API}/claim/${newClaimId}`);
            if (claimResponse.data.claim_details) {
              setClaimDetails(claimResponse.data.claim_details);
            }
          }

        } catch (e) {
          console.error(`Error processing step ${step}:`, e);
        }

        await delay(30000); // 30 second delay between steps
      }

      // All validations complete - Orchestrator approves
      setActiveAgent('orchestrator');
      const approveTimestamp = new Date().toLocaleTimeString('en-GB', { hour12: false });
      addLog(approveTimestamp, 'Orchestrator Agent', 'All 6 validations passed successfully', 'success');
      await delay(2000);

      // Approve claim
      await axios.post(`${API}/claim/${newClaimId}/approve`);
      addLog(approveTimestamp, 'Orchestrator Agent', 'Claim APPROVED - Transferring to Payment Agent', 'success');
      await delay(30000);

      // Payment Agent
      setActiveAgent('payment');
      const paymentTimestamp = new Date().toLocaleTimeString('en-GB', { hour12: false });

      // Process payment
      const paymentResponse = await axios.post(`${API}/claim/${newClaimId}/pay`);

      // Add payment logs
      paymentResponse.data.logs.forEach(log => {
        addLog(log.timestamp, log.agent, log.message, log.log_type);
      });

      // Update claim details with final status
      const finalClaim = await axios.get(`${API}/claim/${newClaimId}`);
      setClaimDetails(finalClaim.data.claim_details);

      await delay(2000);
      addLog(paymentTimestamp, 'Orchestrator Agent', 'Workflow completed successfully! No-touch claim processed.', 'success');

      setWorkflowStatus('completed');
      setActiveAgent(null);

    } catch (e) {
      console.error("Workflow error:", e);
      addLog(new Date().toLocaleTimeString('en-GB', { hour12: false }), 'System', 'Error in workflow: ' + e.message, 'error');
      setWorkflowStatus('idle');
    }
  }, []);

  const resetWorkflow = async () => {
    try {
      await axios.delete(`${API}/claims`);
    } catch (e) {
      console.error("Error clearing claims:", e);
    }
    setWorkflowStatus('idle');
    setCurrentStep(0);
    setLogs([]);
    setClaimId(null);
    setClaimDetails(null);
    setActiveAgent(null);
    fetchScenario();
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC]">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 px-6 py-3">
        <div className="flex items-center justify-between max-w-[1800px] mx-auto">
          <IncomeLogo />
          <div className="flex items-center gap-3">
            {workflowStatus !== 'idle' && (
              <Button
                variant="outline"
                onClick={resetWorkflow}
                className="gap-2 text-sm"
                data-testid="reset-demo-btn"
              >
                <RotateCcw className="w-4 h-4" />
                Reset Demo
              </Button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main style={{ display: 'grid', gridTemplateColumns: '300px 1fr 350px', height: 'calc(100vh - 61px)' }}>
        {/* Left Sidebar - Policy & Flight Info */}
        <aside className="border-r border-slate-200 bg-slate-50/50 p-5 space-y-4 overflow-y-auto">
          <PolicyHolderCard holder={scenario?.policy_holder} />
          <PolicyDetailsCard policy={scenario?.policy_details} />
          <FlightInfoCard flights={scenario?.flight_segments} />
        </aside>

        {/* Center - Agent Workflow */}
        <section className="p-6 overflow-y-auto bg-white/50">
          <div className="space-y-4">
              {/* Orchestrator Agent */}
              <AgentCard
                title="Orchestrator Agent"
                subtitle="Workflow Coordination & Routing"
                icon={Workflow}
                active={activeAgent === 'orchestrator'}
                completed={workflowStatus === 'completed' || (activeAgent !== 'orchestrator' && currentStep > 0)}
                showSpinner={activeAgent === 'orchestrator' && workflowStatus !== 'completed'}
              />

              {/* Claim Processing Agent */}
              <AgentCard
                title="Claim Processing Agent"
                subtitle="6-Step Validation & Analysis"
                icon={ShieldCheck}
                active={activeAgent === 'claim'}
                completed={currentStep >= 6}
                showSpinner={activeAgent === 'claim'}
              />

              {/* Payment Agent */}
              <AgentCard
                title="Payment Agent"
                subtitle="Claim Payment Processing & Transfer"
                icon={Mail}
                active={activeAgent === 'payment'}
                completed={workflowStatus === 'completed'}
                showSpinner={activeAgent === 'payment'}
              />

              {/* Validation Progress - Separate Card Below Agents */}
              <ValidationProgressCard
                steps={validationSteps}
                visible={activeAgent === 'claim' || currentStep > 0}
              />

              {/* Claim Summary */}
              <ClaimSummary claim={claimDetails} visible={workflowStatus === 'completed'} />
            </div>
        </section>

        {/* Right Sidebar - Terminal Log */}
        <aside className="p-4 bg-slate-100/50">
          <TerminalLog logs={logs} />
        </aside>
      </main>

      {/* Footer */}
      <a
        href="https://emergentagent.com"
        target="_blank"
        rel="noopener noreferrer"
        className="fixed bottom-4 right-4 flex items-center gap-2 text-xs text-slate-400 hover:text-slate-600 transition-colors bg-white px-3 py-2 rounded-lg shadow-sm border border-slate-200"
      >
        <img
          src="https://avatars.githubusercontent.com/in/1201222?s=120&u=2686cf91179bbafbc7a71bfbc43004cf9ae1acea&v=4"
          alt="Emergent"
          className="w-5 h-5 rounded"
        />
        Made with Emergent
      </a>
    </div>
  );
}

export default App;
