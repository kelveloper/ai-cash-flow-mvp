import jsPDF from 'jspdf';
import 'jspdf-autotable';

export const generateTransactionReport = (transactions, month) => {
  const doc = new jsPDF();

  // Add header
  doc.setFontSize(22);
  doc.text(`Transaction Report - ${month}`, 14, 22);

  // Add table
  doc.autoTable({
    startY: 30,
    head: [['Date', 'Description', 'Category', 'Amount']],
    body: transactions.map(t => [
      new Date(t.date).toLocaleDateString(),
      t.description,
      t.category,
      `$${t.amount.toFixed(2)}`
    ]),
  });

  // Save the PDF
  doc.save(`transaction-report-${month}.pdf`);
}; 