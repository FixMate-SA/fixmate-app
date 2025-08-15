import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { apiService } from '../../services/api';

const FixerJobFeePayment = ({ outstandingPayments = [] }) => {
  const { user } = useAuth();
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState('');
  const [paymentData, setPaymentData] = useState({});
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showPaymentForm, setShowPaymentForm] = useState(false);
  const [apiDebugInfo, setApiDebugInfo] = useState({});
  
  // Debug API configuration in production
  useEffect(() => {
    if (process.env.NODE_ENV === 'production') {
      const debugInfo = {
        backendUrl: process.env.REACT_APP_BACKEND_URL || 'relative URLs',
        currentHost: window.location.host,
        apiBaseUrl: `${process.env.REACT_APP_BACKEND_URL || ''}/api`,
        paymentEndpoint: `${process.env.REACT_APP_BACKEND_URL || ''}/api/fixer/outstanding-payments`
      };
      setApiDebugInfo(debugInfo);
      console.log('🔍 Payment System API Debug Info:', debugInfo);
    }
  }, []);

  // Calculate total outstanding amount
  const totalOutstanding = outstandingPayments.reduce((sum, payment) => sum + payment.amount, 0);

  const paymentMethods = [
    {
      id: 'card',
      name: 'Credit/Debit Card',
      description: 'Pay instantly with your bank card',
      icon: '💳',
      fee: '2.5% + R1.50',
      processing: 'Instant',
      popular: true
    },
    {
      id: 'eft',
      name: 'EFT (Bank Transfer)',
      description: 'Direct transfer from your bank account',
      icon: '🏦',
      fee: 'Free',
      processing: 'Instant - 24 hours',
      popular: false
    }
  ];

  const handlePaymentMethodSelect = (method) => {
    setSelectedPaymentMethod(method.id);
    setShowPaymentForm(true);
    setError('');
    setSuccess('');
    setPaymentData({});
  };

  const handleCardPayment = async () => {
    if (!paymentData.cardNumber || !paymentData.expiryMonth || !paymentData.expiryYear || !paymentData.cvv || !paymentData.cardHolder) {
      setError('Please fill in all card details');
      return;
    }

    setProcessing(true);
    setError('');

    try {
      const response = await apiService.post('/fixer/payment/card', {
        amount: totalOutstanding,
        card_number: paymentData.cardNumber,
        expiry_month: paymentData.expiryMonth,
        expiry_year: paymentData.expiryYear,
        cvv: paymentData.cvv,
        card_holder: paymentData.cardHolder,
        payment_ids: outstandingPayments.map(p => p.id)
      });

      if (response.data.success) {
        setSuccess(`Payment of R${totalOutstanding.toFixed(2)} successful! Transaction ID: ${response.data.transaction_id}`);
        setShowPaymentForm(false);
        // Refresh the page or update parent component
        setTimeout(() => window.location.reload(), 2000);
      } else {
        setError(response.data.message || 'Payment failed. Please try again.');
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Payment failed. Please check your card details and try again.');
    } finally {
      setProcessing(false);
    }
  };

  const handleEFTPayment = async () => {
    if (!paymentData.accountHolder || !paymentData.bankName) {
      setError('Please fill in your account holder name and bank');
      return;
    }

    setProcessing(true);
    setError('');

    try {
      const response = await apiService.post('/fixer/payment/eft', {
        amount: totalOutstanding,
        account_holder: paymentData.accountHolder,
        bank_name: paymentData.bankName,
        reference: paymentData.reference || `FIXER-${user.id.slice(0, 8)}`,
        payment_ids: outstandingPayments.map(p => p.id)
      });

      if (response.data.success) {
        setSuccess('EFT payment initiated successfully! Please complete the transfer using the banking details provided.');
        setShowPaymentForm(false);
      } else {
        setError(response.data.message || 'EFT payment setup failed. Please try again.');
      }
    } catch (err) {
      setError(err.response?.data?.message || 'EFT payment setup failed. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  const renderCardForm = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Card Holder Name
        </label>
        <input
          type="text"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
          placeholder="John Doe"
          value={paymentData.cardHolder || ''}
          onChange={(e) => setPaymentData({...paymentData, cardHolder: e.target.value})}
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Card Number
        </label>
        <input
          type="text"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
          placeholder="1234 5678 9012 3456"
          maxLength="19"
          value={paymentData.cardNumber || ''}
          onChange={(e) => {
            const value = e.target.value.replace(/\s/g, '').replace(/(.{4})/g, '$1 ').trim();
            setPaymentData({...paymentData, cardNumber: value});
          }}
        />
      </div>
      
      <div className="flex space-x-4">
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Expiry Month
          </label>
          <select
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
            value={paymentData.expiryMonth || ''}
            onChange={(e) => setPaymentData({...paymentData, expiryMonth: e.target.value})}
          >
            <option value="">Month</option>
            {Array.from({length: 12}, (_, i) => i + 1).map(month => (
              <option key={month} value={month.toString().padStart(2, '0')}>
                {month.toString().padStart(2, '0')}
              </option>
            ))}
          </select>
        </div>
        
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Expiry Year
          </label>
          <select
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
            value={paymentData.expiryYear || ''}
            onChange={(e) => setPaymentData({...paymentData, expiryYear: e.target.value})}
          >
            <option value="">Year</option>
            {Array.from({length: 10}, (_, i) => new Date().getFullYear() + i).map(year => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>
        </div>
        
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            CVV
          </label>
          <input
            type="text"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
            placeholder="123"
            maxLength="4"
            value={paymentData.cvv || ''}
            onChange={(e) => setPaymentData({...paymentData, cvv: e.target.value.replace(/\D/g, '')})}
          />
        </div>
      </div>
      
      <div className="bg-gray-50 p-3 rounded-md">
        <div className="flex justify-between text-sm">
          <span>Service Fee:</span>
          <span>R{totalOutstanding.toFixed(2)}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span>Processing Fee (2.5% + R1.50):</span>
          <span>R{((totalOutstanding * 0.025) + 1.50).toFixed(2)}</span>
        </div>
        <div className="flex justify-between font-bold border-t pt-2 mt-2">
          <span>Total:</span>
          <span>R{(totalOutstanding + (totalOutstanding * 0.025) + 1.50).toFixed(2)}</span>
        </div>
      </div>
      
      <button
        onClick={handleCardPayment}
        disabled={processing}
        className="w-full bg-orange-600 hover:bg-orange-700 disabled:opacity-50 text-white py-3 px-4 rounded-md font-medium transition-colors"
      >
        {processing ? (
          <div className="flex items-center justify-center space-x-2">
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            <span>Processing Payment...</span>
          </div>
        ) : (
          `Pay R${(totalOutstanding + (totalOutstanding * 0.025) + 1.50).toFixed(2)}`
        )}
      </button>
    </div>
  );

  const renderEFTForm = () => (
    <div className="space-y-4">
      <div className="bg-blue-50 p-4 rounded-md">
        <h4 className="font-semibold text-blue-900 mb-2">FixMate-SA Banking Details</h4>
        <div className="text-sm text-blue-800 space-y-1">
          <div><strong>Bank:</strong> First National Bank (FNB)</div>
          <div><strong>Account Name:</strong> FixMate-SA (Pty) Ltd</div>
          <div><strong>Account Number:</strong> 1234567890</div>
          <div><strong>Branch Code:</strong> 250655</div>
          <div><strong>Reference:</strong> FIXER-{user.id.slice(0, 8)}-FEE</div>
          <div><strong>Amount:</strong> R{totalOutstanding.toFixed(2)}</div>
        </div>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Your Full Name (as per bank account)
        </label>
        <input
          type="text"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="John Doe"
          value={paymentData.accountHolder || ''}
          onChange={(e) => setPaymentData({...paymentData, accountHolder: e.target.value})}
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Your Bank Name
        </label>
        <select
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={paymentData.bankName || ''}
          onChange={(e) => setPaymentData({...paymentData, bankName: e.target.value})}
        >
          <option value="">Select your bank</option>
          <option value="FNB">First National Bank (FNB)</option>
          <option value="ABSA">ABSA Bank</option>
          <option value="Standard Bank">Standard Bank</option>
          <option value="Nedbank">Nedbank</option>
          <option value="Capitec">Capitec Bank</option>
          <option value="Discovery Bank">Discovery Bank</option>
          <option value="TymeBank">TymeBank</option>
          <option value="African Bank">African Bank</option>
          <option value="Investec">Investec</option>
          <option value="Other">Other</option>
        </select>
      </div>
      
      <div className="bg-yellow-50 p-3 rounded-md">
        <p className="text-sm text-yellow-800">
          <strong>Instructions:</strong>
        </p>
        <ol className="text-sm text-yellow-800 list-decimal list-inside mt-2 space-y-1">
          <li>Transfer R{totalOutstanding.toFixed(2)} to the account details above</li>
          <li>Use the reference number: <strong>FIXER-{user.id.slice(0, 8)}-FEE</strong></li>
          <li>Keep your proof of payment</li>
          <li>Payment will be verified within 24 hours</li>
        </ol>
      </div>
      
      <button
        onClick={handleEFTPayment}
        disabled={processing}
        className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white py-3 px-4 rounded-md font-medium transition-colors"
      >
        {processing ? (
          <div className="flex items-center justify-center space-x-2">
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            <span>Setting up EFT...</span>
          </div>
        ) : (
          'Confirm EFT Payment Details'
        )}
      </button>
    </div>
  );

  if (outstandingPayments.length === 0) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
        <div className="text-green-400 text-4xl mb-4">✅</div>
        <h3 className="text-lg font-medium text-green-900 mb-2">All Payments Up to Date</h3>
        <p className="text-green-600">You have no outstanding service fees. Keep up the great work!</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Outstanding Payments Summary */}
      <div className="bg-orange-50 border border-orange-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-orange-900 mb-4">Outstanding Service Fees</h3>
        
        <div className="space-y-3 mb-4">
          {outstandingPayments.map((payment) => (
            <div key={payment.id} className="flex justify-between items-center bg-white p-3 rounded border">
              <div>
                <p className="font-medium">Service Fee - {payment.description}</p>
                <p className="text-sm text-gray-500">
                  Due: {new Date(payment.due_date).toLocaleDateString()}
                  {payment.status === 'overdue' && (
                    <span className="ml-2 text-red-600 font-medium">OVERDUE</span>
                  )}
                </p>
              </div>
              <div className="text-lg font-bold text-orange-600">
                R{payment.amount.toFixed(2)}
              </div>
            </div>
          ))}
        </div>
        
        <div className="border-t pt-4">
          <div className="flex justify-between items-center">
            <span className="text-lg font-semibold">Total Outstanding:</span>
            <span className="text-2xl font-bold text-orange-600">R{totalOutstanding.toFixed(2)}</span>
          </div>
        </div>
      </div>

      {/* Payment Methods */}
      {!showPaymentForm && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold mb-4">Choose Payment Method</h3>
          
          <div className="space-y-4">
            {paymentMethods.map((method) => (
              <div
                key={method.id}
                onClick={() => handlePaymentMethodSelect(method)}
                className={`p-4 border-2 rounded-lg cursor-pointer transition-all hover:border-orange-300 ${
                  method.popular 
                    ? 'border-orange-200 bg-orange-50' 
                    : 'border-gray-200 bg-gray-50'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">{method.icon}</span>
                    <div>
                      <h4 className="font-semibold flex items-center">
                        {method.name}
                        {method.popular && (
                          <span className="ml-2 text-xs bg-orange-600 text-white px-2 py-1 rounded-full">
                            POPULAR
                          </span>
                        )}
                      </h4>
                      <p className="text-sm text-gray-600">{method.description}</p>
                    </div>
                  </div>
                  <div className="text-right text-sm text-gray-500">
                    <div>Fee: {method.fee}</div>
                    <div>{method.processing}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Payment Form */}
      {showPaymentForm && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">
              {selectedPaymentMethod === 'card' ? 'Credit/Debit Card Payment' : 'EFT Bank Transfer'}
            </h3>
            <button
              onClick={() => {
                setShowPaymentForm(false);
                setSelectedPaymentMethod('');
                setPaymentData({});
                setError('');
              }}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕ Cancel
            </button>
          </div>
          
          {selectedPaymentMethod === 'card' && renderCardForm()}
          {selectedPaymentMethod === 'eft' && renderEFTForm()}
        </div>
      )}

      {/* Success/Error Messages */}
      {success && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-md">
          {success}
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
          {error}
        </div>
      )}

      {/* Payment Info */}
      <div className="bg-blue-50 rounded-lg p-4">
        <h4 className="font-semibold text-blue-900 mb-2">💡 About Service Fees</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>✅ R20 service fee per completed job helps maintain the platform</li>
          <li>✅ Payment due within 7 days of job completion</li>
          <li>✅ Secure payment processing with bank-level encryption</li>
          <li>✅ Multiple payment options for your convenience</li>
          <li>⚠️ Late payments may affect your ability to receive new jobs</li>
        </ul>
      </div>
    </div>
  );
};

export default FixerJobFeePayment;