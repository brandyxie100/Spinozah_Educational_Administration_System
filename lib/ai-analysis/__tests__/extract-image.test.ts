/**
 * @jest-environment node
 */
import { extractTextFromImage } from '../extract-image';

const mockRecognize = jest.fn();

jest.mock('tesseract.js', () => ({
  recognize: (...args: unknown[]) => mockRecognize(...args),
}));

describe('extractTextFromImage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('test_extractTextFromImage_validBuffer_returnsTrimmedText', async () => {
    mockRecognize.mockResolvedValue({
      data: { text: '  Scanned exam question  ' },
    });

    const text = await extractTextFromImage(Buffer.from('fake-image'));

    expect(text).toBe('Scanned exam question');
    expect(mockRecognize).toHaveBeenCalledWith(Buffer.from('fake-image'), 'eng');
  });

  it('test_extractTextFromImage_ocrFails_propagatesError', async () => {
    mockRecognize.mockRejectedValue(new Error('OCR failed'));

    await expect(extractTextFromImage(Buffer.from('bad-image'))).rejects.toThrow(
      'OCR failed',
    );
  });
});
