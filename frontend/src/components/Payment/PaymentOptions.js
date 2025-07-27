import React, { useState } from 'react';
import { useLanguage } from '../../contexts/LanguageContext';
import { apiService } from '../../services/api';

const PaymentOptions = ({ amount, description, onPaymentSuccess, onPaymentCancel }) => {
  const { t, formatCurrency } = useLanguage();
  const [selectedMethod, setSelectedMethod] = useState('');
  const [paymentData, setPaymentData] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const paymentMethods = [
    {
      id: 'eft',
      name: t('payWithEFT', 'Pay with EFT'),
      description: 'Direct bank transfer - Most popular in SA',
      icon: '🏦',
      fees: 'Free',
      processing: 'Instant',
      color: 'bg-blue-100 text-blue-800 border-blue-200'
    },
    {
      id: 'card',
      name: t('payWithCard', 'Pay with Card'),
      description: 'Credit or Debit Card',
      icon: '💳',
      fees: '2.5%',
      processing: 'Instant',
      color: 'bg-green-100 text-green-800 border-green-200'
    },
    {
      id: 'airtime',
      name: t('payWithAirtime', 'Pay with Airtime'),
      description: 'Use airtime credit as payment',
      icon: '📱',
      fees: '5%',
      processing: '2-5 minutes',
      color: 'bg-purple-100 text-purple-800 border-purple-200'
    },
    {
      id: 'cash',
      name: t('cashCollection', 'Cash Collection'),
      description: 'Pay at Shoprite, Pick n Pay, Checkers',
      icon: '💰',
      fees: 'R5',
      processing: 'Up to 24 hours',
      color: 'bg-yellow-100 text-yellow-800 border-yellow-200'
    },
    {
      id: 'stokvel',
      name: t('stokvelPayment', 'Stokvel Payment'),
      description: 'Community savings group payment',
      icon: '👥',
      fees: 'Free',
      processing: '1-3 days',
      color: 'bg-orange-100 text-orange-800 border-orange-200'
    },
    {
      id: 'layby',
      name: 'Lay-by Payment',
      description: 'Pay in installments',
      icon: '📅',
      fees: '1%/month',
      processing: 'Flexible',
      color: 'bg-indigo-100 text-indigo-800 border-indigo-200'
    }
  ];

  const handleMethodSelect = (method) => {
    setSelectedMethod(method.id);
    setError('');
  };

  const handlePayment = async () => {
    setLoading(true);
    setError('');

    try {
      let response;
      
      switch (selectedMethod) {
        case 'eft':
          response = await apiService.createEFTPayment(amount, description, paymentData);
          break;
        case 'card':
          response = await apiService.createCardPayment(amount, description, paymentData);
          break;
        case 'airtime':
          response = await apiService.createAirtimePayment(paymentData.phoneNumber, amount, description);
          break;
        case 'cash':
          response = await apiService.createCashPayment(paymentData.location, amount, description);
          break;
        case 'stokvel':
          response = await apiService.createStokvelPayment(paymentData.stokvelName, amount, description);
          break;
        case 'layby':
          response = await apiService.createLaybyPayment(amount, paymentData.deposit, description, paymentData.installments);
          break;
        default:
          throw new Error('Invalid payment method selected');
      }

      if (response.data.success) {
        onPaymentSuccess(response.data);
      } else {
        setError(response.data.error || 'Payment failed');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Payment processing failed');
    } finally {
      setLoading(false);
    }
  };

  const renderPaymentForm = () => {
    if (!selectedMethod) return null;

    const method = paymentMethods.find(m => m.id === selectedMethod);

    return (
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
          <span className="text-2xl">{method.icon}</span>
          <span>{method.name}</span>
        </h3>

        {selectedMethod === 'eft' && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Bank Account Details
              </label>
              <div className="bg-white p-4 rounded border">
                <p className="text-sm font-mono">
                  <strong>Bank:</strong> First National Bank<br/>
                  <strong>Account Name:</strong> FixMate-SA (Pty) Ltd<br/>
                  <strong>Account Number:</strong> 1234567890<br/>
                  <strong>Branch Code:</strong> 250655<br/>
                  <strong>Reference:</strong> {description}
                </p>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Your Name (for verification)
              </label>
              <input
                type="text"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter your full name"
                value={paymentData.name || ''}
                onChange={(e) => setPaymentData({...paymentData, name: e.target.value})}
              />
            </div>
          </div>
        )}

        {selectedMethod === 'airtime' && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Phone Number
              </label>
              <input
                type="tel"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="e.g., 0821234567"
                value={paymentData.phoneNumber || ''}
                onChange={(e) => setPaymentData({...paymentData, phoneNumber: e.target.value})}
              />
            </div>
            <div className="bg-purple-50 p-3 rounded-md">
              <p className="text-sm text-purple-800">
                📱 <strong>Instructions:</strong> You'll receive SMS instructions to transfer airtime worth {formatCurrency(amount)} to our payment number.
              </p>
            </div>
          </div>
        )}

        {selectedMethod === 'cash' && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Your Location/City
              </label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-500"
                value={paymentData.location || ''}
                onChange={(e) => setPaymentData({...paymentData, location: e.target.value})}
              >
                <option value="">Select your city</option>
                <option value="johannesburg">Johannesburg</option>
                <option value="cape_town">Cape Town</option>
                <option value="durban">Durban</option>
                <option value="pretoria">Pretoria</option>
                <option value="port_elizabeth">Port Elizabeth</option>
                <option value="bloemfontein">Bloemfontein</option>
              </select>
            </div>
            <div className="bg-yellow-50 p-3 rounded-md">
              <p className="text-sm text-yellow-800">
                🏪 <strong>Available at:</strong> Shoprite, Pick n Pay, Checkers stores near you. You'll get a reference number to use at the till.
              </p>
            </div>
          </div>
        )}

        {selectedMethod === 'stokvel' && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Stokvel Name
              </label>
              <input
                type="text"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
                placeholder="Enter your stokvel name"
                value={paymentData.stokvelName || ''}
                onChange={(e) => setPaymentData({...paymentData, stokvelName: e.target.value})}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Contact Person
              </label>
              <input
                type="text"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
                placeholder="Stokvel coordinator name"
                value={paymentData.contactPerson || ''}
                onChange={(e) => setPaymentData({...paymentData, contactPerson: e.target.value})}
              />
            </div>
            <div className="bg-orange-50 p-3 rounded-md">
              <p className="text-sm text-orange-800">
                👥 <strong>Note:</strong> Your stokvel coordinator will be contacted to approve this payment.
              </p>
            </div>
          </div>
        )}

        {selectedMethod === 'layby' && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Deposit Amount
              </label>
              <input
                type="number"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="Minimum 20%"
                min={amount * 0.2}
                max={amount * 0.8}
                value={paymentData.deposit || ''}
                onChange={(e) => setPaymentData({...paymentData, deposit: parseFloat(e.target.value)})}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Number of Installments
              </label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                value={paymentData.installments || ''}
                onChange={(e) => setPaymentData({...paymentData, installments: parseInt(e.target.value)})}
              >
                <option value="">Select installments</option>
                <option value="3">3 months</option>
                <option value="6">6 months</option>
                <option value="12">12 months</option>
              </select>
            </div>
            {paymentData.deposit && paymentData.installments && (
              <div className="bg-indigo-50 p-3 rounded-md">
                <p className="text-sm text-indigo-800">
                  📅 <strong>Payment Plan:</strong><br/>
                  Deposit: {formatCurrency(paymentData.deposit)}<br/>
                  Monthly: {formatCurrency((amount - paymentData.deposit) / paymentData.installments)}<br/>
                  Total: {formatCurrency(amount + (amount * 0.01 * paymentData.installments))}
                </p>
              </div>
            )}
          </div>
        )}

        <div className="flex items-center justify-between mt-6">
          <button
            onClick={onPaymentCancel}
            className="px-4 py-2 text-gray-600 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
          >
            {t('cancel', 'Cancel')}
          </button>
          <button
            onClick={handlePayment}
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Processing...</span>
              </div>
            ) : (
              `Pay ${formatCurrency(amount)}`
            )}
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            {t('paymentOptions', 'Payment Options')}
          </h2>
          <p className="text-gray-600 mb-6">
            Choose your preferred payment method for {formatCurrency(amount)}
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {paymentMethods.map((method) => (
              <div
                key={method.id}
                onClick={() => handleMethodSelect(method)}
                className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                  selectedMethod === method.id
                    ? method.color
                    : 'bg-gray-50 border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">{method.icon}</span>
                    <div>
                      <h3 className="font-semibold">{method.name}</h3>
                      <p className="text-sm text-gray-600">{method.description}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-500">Fee: {method.fees}</p>
                    <p className="text-xs text-gray-500">{method.processing}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {error && (
            <div className="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
              {error}
            </div>
          )}

          {renderPaymentForm()}
        </div>
      </div>

      {/* Payment Methods Info */}
      <div className="mt-6 bg-blue-50 rounded-lg p-4">
        <h3 className="font-semibold text-blue-900 mb-2">💡 Why Choose FixMate-SA Payments?</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>✅ Multiple payment options designed for South Africans</li>
          <li>✅ Secure processing with bank-level encryption</li>
          <li>✅ Community-friendly options (stokvel, cash collection)</li>
          <li>✅ Flexible payment plans available</li>
          <li>✅ No hidden fees - transparent pricing</li>
        </ul>
      </div>
    </div>
  );
};

export default PaymentOptions;