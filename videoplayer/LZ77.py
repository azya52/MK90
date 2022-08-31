PART_SIZE = 480

class LZ77Compressor:   
    def __init__(self, window_size, lookahead_buffer_size):
        self.window_size = window_size
        self.lookahead_buffer_size = lookahead_buffer_size
        self.prev_data = None
        
    def compareFrames(self, data):
        end1 = PART_SIZE
        end2 = PART_SIZE * 2
        if self.prev_data:
            while end1 > 0 and self.prev_data[end1-1] == data[end1-1]:
                end1 -= 1
            while end2 > PART_SIZE and self.prev_data[end2-1] == data[end2-1]:
                end2 -= 1
        return (end1, end2)
        
    def findFrameOverlap(self, data, pos):
        len = 0
        if self.prev_data:
            max_pos = (pos // PART_SIZE + 1) * PART_SIZE - 1
            while data[pos] == self.prev_data[pos] and len < 255 and pos < max_pos:
                pos += 1
                len += 1
        return len
        
    def compress(self, data):
        output = bytearray()
        head_pos = 0
        k = 0
        ends = self.compareFrames(data);
        for p in range(2):
            dataPart = data[PART_SIZE * p : ends[p]]
            i = 0
            while i < len(dataPart):
                if k % 8 == 0:
                    head_pos = len(output)
                    output.append(0x00)
                overlap = self.findFrameOverlap(data, i + PART_SIZE * p)
                
                match_count = 0
                match_bytes = 0
                while (match_count < (overlap - 1) and match_bytes < 2):
                    match = self.findLongestMatch(dataPart, i + match_count)
                    match_count += match[1] if match else 1
                    match_bytes += 1   
                    
                if (overlap in range(2,16) or overlap in range(18,26)) and (overlap-1) >= (match_count - match_bytes):
                    output[head_pos] += (1 << k % 8)
                    output.append(overlap)
                    i += overlap
                elif overlap > 2 and (overlap-2) >= (match_count - match_bytes):
                    output[head_pos] += (1 << k % 8)
                    output.append(0x1C)
                    output.append(overlap)
                    i += overlap
                else:
                    match = self.findLongestMatch(dataPart, i)
                    if match: 
                        output[head_pos] += (1 << k % 8)
                        (bestMatchDistance, bestMatchLength) = match
                        if (bestMatchLength > 15 and bestMatchDistance < 15):
                            bestMatchLength = 15
                        app = ((15-(bestMatchLength-2) << 4) & 0xF0) + (-bestMatchDistance & 0x0F);
                        output.append(app)
                        i += bestMatchLength
                    else: 
                        output.append(dataPart[i])
                        i += 1
                k += 1
                
            if k % 8 == 0:
                head_pos = len(output)
                output.append(0x00)
            output[head_pos] += (1 << k % 8)         
            output.append(0x1E)
            k += 1
            
        if len(output) > PART_SIZE * 2:
            output = bytearray(b'\xFF\x1A') + data

        self.prev_data = data
        return output
        
    def findLongestMatch(self, data, current_position):
        #original code of this method https://github.com/manassra/LZ77-Compressor
        """ 
        Finds the longest match to a substring starting at the current_position 
        in the lookahead buffer from the history window
        """
        end_of_buffer = min(current_position + self.lookahead_buffer_size + 1, len(data) + 1)

        best_match_distance = -1
        best_match_length = -1

        # Optimization: Only consider substrings of length 2 and greater, and just 
        # output any substring of length 1 (8 bits uncompressed is better than 13 bits
        # for the flag, distance, and length)
        for j in range(current_position + 2, end_of_buffer):
        
            start_index = max(0, current_position - self.window_size)
            substring = data[current_position:j]
            len_substr = len(substring)
            for i in range(start_index, current_position):

                repetitions = len_substr // (current_position - i)
                last = len_substr % (current_position - i)
                matched_string = data[i:current_position] * repetitions + data[i:i+last]
                
                if matched_string == substring and len_substr > best_match_length:
                    best_match_distance = current_position - i 
                    best_match_length = len_substr

        if best_match_distance > 0 and best_match_length > 0:
            return (best_match_distance, best_match_length)
        return None