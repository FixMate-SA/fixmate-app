import React, { useState, useEffect } from 'react';
import { useLanguage } from '../../contexts/LanguageContext';
import { useAuth } from '../../contexts/AuthContext';
import { apiService } from '../../services/api';
import FixerJobFeePayment from './FixerJobFeePayment';

// FixerPaymentManager - Payment System v2.3.0 - Heroku Production Fix
const FixerPaymentManager = ({ fixerId: propFixerId, isAdmin = false }) => {
  const { t } = useLanguage();
  const { user } = useAuth();
  const [paymentStatus, setPaymentStatus] = useState(null);
  const [paymentHistory, setPaymentHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [settling, setSettling] = useState(null);
  const [settlementData, setSettlementData] = useState({
    payment_method: '',
    reference: ''
  });

  // Use prop fixerId if provided (admin use), otherwise use current user's ID
  const fixerId = propFixerId || user?.id;

  useEffect(() => {
    if (fixerId) {
      fetchPaymentData();
    } else {
      setError('No fixer ID available');
      setLoading(false);
    }
  }, [fixerId]);

  const fetchPaymentData = async () => {
    try {
      setLoading(true);
      
      // Try to fetch fixer payment data from the database
      try {
        // First create test payments if needed (development only)
        await apiService.post('/fixer/create-test-payments');
        
        // Get outstanding payments from fixer_payments table
        const outstandingResponse = await apiService.get('/fixer/outstanding-payments');
        const historyResponse = await apiService.get('/fixer/payment-history');

        setPaymentStatus({
          payment_status: 'pending',
          total_outstanding: outstandingResponse.data?.total_outstanding || 0,
          can_receive_jobs: outstandingResponse.data?.can_receive_jobs !== false,
          overdue_payments: outstandingResponse.data?.overdue_count || 0,
          outstanding_payments: outstandingResponse.data?.payments || []
        });
        
        setPaymentHistory(historyResponse.data?.payments || []);
        setError('');
      } catch (apiError) {
        console.log('Payment API not available, showing basic interface');
        setPaymentStatus({
          payment_status: 'pending',
          total_outstanding: 0,
          pending_amount: 0,
          available_balance: 0,
          outstanding_payments: []
        });
        setPaymentHistory([]);
        setError('');
      }
    } catch (err) {
      console.error('Error fetching payment data:', err);
      setError('Failed to load payment information');
    } finally {
      setLoading(false);
    }
  };

  const handleSettlePayment = async (paymentId) => {
    try {
      setSettling(paymentId);
      
      const response = await apiService.post(`/fixer/payment/${paymentId}/settle`, {
        payment_method: settlementData.payment_method,
        reference: settlementData.reference
      });

      if (response.success) {
        await fetchPaymentData(); // Refresh data
        setSettlementData({ payment_method: '', reference: '' });
        setSettling(null);
      } else {
        setError(response.error || 'Failed to settle payment');
      }
    } catch (err) {
      console.error('Error settling payment:', err);
      setError('Failed to settle payment');
    } finally {
      setSettling(null);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'current':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'overdue':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'blocked':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    }
  };

  const getPaymentStatusColor = (status) => {
    switch (status) {
      case 'paid':
        return 'bg-orange-100 text-orange-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'overdue':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="p-6 bg-white rounded-lg shadow-sm">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-6 bg-gray-200 rounded w-2/3 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-white rounded-lg shadow-sm">
        <div className="text-red-600 text-center">
          <p>{error}</p>
          <button
            onClick={fetchPaymentData}
            className="mt-2 px-4 py-2 bg-red-100 text-red-700 rounded hover:bg-red-200"
          >
            {t('retry', 'Retry')}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Real Payment Interface for Outstanding Fees */}
      <FixerJobFeePayment outstandingPayments={paymentStatus?.outstanding_payments || []} />
      
      {/* Payment Status Overview */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">
          {t('paymentStatus', 'Payment Status')}
        </h3>
        
        {paymentStatus && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className={`p-4 rounded-lg border-2 ${getStatusColor(paymentStatus.payment_status)}`}>
                <div className="text-sm font-medium">
                  {t('currentStatus', 'Current Status')}
                </div>
                <div className="text-lg font-bold capitalize">
                  {paymentStatus.payment_status}
                </div>
              </div>
              
              <div className="p-4 bg-orange-100 text-orange-800 border-2 border-orange-200 rounded-lg">
                <div className="text-sm font-medium">
                  {t('outstandingBalance', 'Outstanding Balance')}
                </div>
                <div className="text-lg font-bold">
                  R{(paymentStatus.total_outstanding || 0).toFixed(2)}
                </div>
              </div>
              
              <div className={`p-4 rounded-lg border-2 ${
                paymentStatus.can_receive_jobs 
                  ? 'bg-orange-100 text-orange-800 border-orange-200' 
                  : 'bg-red-100 text-red-800 border-red-200'
              }`}>
                <div className="text-sm font-medium">
                  {t('jobEligibility', 'Job Eligibility')}
                </div>
                <div className="text-lg font-bold">
                  {paymentStatus.can_receive_jobs 
                    ? t('eligible', 'Eligible') 
                    : t('blocked', 'Blocked')
                  }
                </div>
              </div>
            </div>

            {paymentStatus.overdue_payments > 0 && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-center">
                  <span className="text-red-600 mr-2">⚠️</span>
                  <span className="text-red-700 font-medium">
                    {paymentStatus.overdue_payments} overdue payment(s). 
                    Job assignment blocked until payments are settled.
                  </span>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Outstanding Payments */}
      {paymentStatus?.outstanding_payments?.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold mb-4">
            {t('outstandingPayments', 'Outstanding Payments')}
          </h3>
          
          <div className="space-y-3">
            {paymentStatus.outstanding_payments.map((payment) => (
              <div key={payment.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`px-2 py-1 rounded text-sm font-medium ${
                        getPaymentStatusColor(payment.status)
                      }`}>
                        {payment.status.toUpperCase()}
                      </span>
                      <span className="text-lg font-bold">
                        R{payment.amount.toFixed(2)}
                      </span>
                    </div>
                    
                    <p className="text-gray-600 text-sm mb-2">
                      {payment.description}
                    </p>
                    
                    {payment.due_date && (
                      <p className="text-sm text-gray-500">
                        Due: {new Date(payment.due_date).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                  
                  {isAdmin && payment.status !== 'paid' && (
                    <div className="ml-4">
                      {settling === payment.id ? (
                        <div className="space-y-2 w-48">
                          <select
                            value={settlementData.payment_method}
                            onChange={(e) => setSettlementData({
                              ...settlementData,
                              payment_method: e.target.value
                            })}
                            className="w-full p-2 border border-gray-300 rounded text-sm"
                          >
                            <option value="">Payment Method</option>
                            <option value="cash">Cash</option>
                            <option value="eft">EFT</option>
                            <option value="card">Card</option>
                            <option value="airtime">Airtime</option>
                          </select>
                          
                          <input
                            type="text"
                            placeholder="Reference Number"
                            value={settlementData.reference}
                            onChange={(e) => setSettlementData({
                              ...settlementData,
                              reference: e.target.value
                            })}
                            className="w-full p-2 border border-gray-300 rounded text-sm"
                          />
                          
                          <div className="flex gap-2">
                            <button
                              onClick={() => handleSettlePayment(payment.id)}
                              disabled={!settlementData.payment_method || !settlementData.reference}
                              className="flex-1 px-3 py-1 bg-orange-600 text-white rounded text-sm hover:bg-orange-700 disabled:bg-gray-300"
                            >
                              Settle
                            </button>
                            <button
                              onClick={() => setSettling(null)}
                              className="flex-1 px-3 py-1 bg-gray-300 text-gray-700 rounded text-sm hover:bg-gray-400"
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      ) : (
                        <button
                          onClick={() => setSettling(payment.id)}
                          className="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                        >
                          {t('settlePayment', 'Settle Payment')}
                        </button>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Payment History */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">
          {t('paymentHistory', 'Payment History')}
        </h3>
        
        {paymentHistory.length === 0 ? (
          <p className="text-gray-500 text-center py-8">
            {t('noPaymentHistory', 'No payment history found')}
          </p>
        ) : (
          <div className="space-y-3">
            {paymentHistory.map((payment) => (
              <div key={payment.id} className="border-b border-gray-100 pb-3 last:border-0">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        getPaymentStatusColor(payment.status)
                      }`}>
                        {payment.status.toUpperCase()}
                      </span>
                      <span className="font-bold">R{payment.amount.toFixed(2)}</span>
                      {payment.payment_method && (
                        <span className="text-gray-500 text-sm">
                          via {payment.payment_method.toUpperCase()}
                        </span>
                      )}
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-1">
                      {payment.description}
                    </p>
                    
                    <div className="text-xs text-gray-500 flex gap-4">
                      <span>Created: {new Date(payment.created_at).toLocaleDateString()}</span>
                      {payment.paid_date && (
                        <span>Paid: {new Date(payment.paid_date).toLocaleDateString()}</span>
                      )}
                      {payment.payment_reference && (
                        <span>Ref: {payment.payment_reference}</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default FixerPaymentManager;