/**
 * @jest-environment node
 */
import { extractTextFromPdf } from '../extract-pdf';

const mockDestroy = jest.fn().mockResolvedValue(undefined);
const mockGetText = jest.fn();

jest.mock('pdf-parse', () => ({
  PDFParse: jest.fn().mockImplementation(() => ({
    getText: mockGetText,
    destroy: mockDestroy,
  })),
}));

describe('extractTextFromPdf', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('test_extractTextFromPdf_validBuffer_returnsTrimmedText', async () => {
    mockGetText.mockResolvedValue({ text: '  Exam page content  \n' });

    const text = await extractTextFromPdf(Buffer.from('fake-pdf'));

    expect(text).toBe('Exam page content');
    expect(mockDestroy).toHaveBeenCalled();
  });

  it('test_extractTextFromPdf_emptyText_returnsEmptyString', async () => {
    mockGetText.mockResolvedValue({ text: '   ' });

    const text = await extractTextFromPdf(Buffer.from('fake-pdf'));

    expect(text).toBe('');
  });

  it('test_extractTextFromPdf_parserFails_propagatesError', async () => {
    mockGetText.mockRejectedValue(new Error('PDF parse failed'));

    await expect(extractTextFromPdf(Buffer.from('bad-pdf'))).rejects.toThrow(
      'PDF parse failed',
    );
    expect(mockDestroy).toHaveBeenCalled();
  });
});
