#!/usr/bin/env python3
"""
Universal JSON Stream Parser
Converts malformed JSON streams (like intel_gpu_top output) into proper JSON format
Handles linebreaks, spaces, and multiple JSON objects in a single stream
"""

import json
import sys
import re
from datetime import datetime

class UniversalJSONParser:
    def __init__(self):
        self.buffer = ""
        self.brace_count = 0
        self.in_string = False
        self.escape_next = False
        
    def reset(self):
        """Reset parser state"""
        self.buffer = ""
        self.brace_count = 0
        self.in_string = False
        self.escape_next = False
    
    def add_char(self, char):
        """Add a character to the buffer and return complete JSON objects"""
        # Skip standalone commas and whitespace when not inside a JSON object
        if self.brace_count == 0 and char in ',\n\r\t ':
            return None
            
        self.buffer += char
        
        # Track string state to avoid counting braces inside strings
        if not self.escape_next:
            if char == '"':
                self.in_string = not self.in_string
            elif char == '\\' and self.in_string:
                self.escape_next = True
                return None
        else:
            self.escape_next = False
            return None
        
        # Only count braces outside of strings
        if not self.in_string:
            if char == '{':
                self.brace_count += 1
            elif char == '}':
                self.brace_count -= 1
                
                # Check if we have a complete JSON object
                if self.brace_count == 0 and self.buffer.strip():
                    complete_obj = self.buffer.strip()
                    self.reset()
                    return self.clean_and_parse_json(complete_obj)
        
        return None
    
    def clean_and_parse_json(self, json_str):
        """Clean and parse a JSON string"""
        try:
            # Remove trailing commas before closing braces/brackets
            json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
            
            # Parse the JSON
            parsed = json.loads(json_str)
            return parsed
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}", file=sys.stderr)
            print(f"Problematic JSON: {json_str[:200]}...", file=sys.stderr)
            return None
    
    def process_stream(self, input_stream, output_format='pretty'):
        """Process a stream of characters and yield complete JSON objects"""
        try:
            while True:
                char = input_stream.read(1)
                if not char:
                    break
                
                json_obj = self.add_char(char)
                if json_obj is not None:
                    yield json_obj
        except KeyboardInterrupt:
            print("\nStream processing stopped by user", file=sys.stderr)
        except Exception as e:
            print(f"Stream processing error: {e}", file=sys.stderr)
    
    def format_output(self, json_obj, output_format='pretty'):
        """Format JSON object for output"""
        if output_format == 'compact':
            return json.dumps(json_obj, separators=(',', ':'))
        elif output_format == 'pretty':
            return json.dumps(json_obj, indent=2)
        elif output_format == 'raw':
            return json_obj
        else:
            return json.dumps(json_obj)

def main():
    import argparse
    import subprocess
    
    parser = argparse.ArgumentParser(description='Universal JSON Stream Parser')
    parser.add_argument('--command', '-c', help='Command to run and parse output from')
    parser.add_argument('--input', '-i', help='Input file to parse (use - for stdin)')
    parser.add_argument('--output', '-o', choices=['pretty', 'compact', 'raw'], 
                       default='pretty', help='Output format')
    parser.add_argument('--intel-gpu', action='store_true', 
                       help='Parse intel_gpu_top output with default settings')
    parser.add_argument('--device-filter', '-d', 
                       help='Device filter for intel_gpu_top (e.g., sys:/sys/devices/pci0000:00/0000:00:02.0)')
    parser.add_argument('--interval', '-s', type=int, default=1000,
                       help='Sampling interval in milliseconds for intel_gpu_top')
    parser.add_argument('--extract', '-e', nargs='+',
                       help='Extract specific fields from JSON (e.g., frequency.actual power.GPU)')
    parser.add_argument('--count', '-n', type=int,
                       help='Stop after parsing N objects')
    
    args = parser.parse_args()
    
    json_parser = UniversalJSONParser()
    input_stream = None
    
    try:
        # Determine input source
        if args.intel_gpu:
            # Build intel_gpu_top command
            cmd = ['intel_gpu_top', '-J', '-s', str(args.interval)]
            if args.device_filter:
                cmd.extend(['-d', args.device_filter])
            
            print(f"Running: {' '.join(cmd)}", file=sys.stderr)
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
            input_stream = process.stdout
            
        elif args.command:
            # Run custom command
            process = subprocess.Popen(args.command.split(), stdout=subprocess.PIPE, text=True)
            input_stream = process.stdout
            
        elif args.input and args.input != '-':
            # Read from file
            input_stream = open(args.input, 'r')
            
        else:
            # Read from stdin
            input_stream = sys.stdin
        
        # Process the stream
        count = 0
        for json_obj in json_parser.process_stream(input_stream):
            count += 1
            
            # Extract specific fields if requested
            if args.extract:
                extracted = {}
                for field_path in args.extract:
                    value = json_obj
                    for key in field_path.split('.'):
                        if isinstance(value, dict) and key in value:
                            value = value[key]
                        else:
                            value = None
                            break
                    extracted[field_path] = value
                json_obj = extracted
            
            # Add metadata
            if args.output != 'raw':
                output_obj = {
                    'timestamp': datetime.now().isoformat(),
                    'sequence': count,
                    'data': json_obj
                }
            else:
                output_obj = json_obj
            
            # Output the result
            print(json_parser.format_output(output_obj, args.output))
            
            # Stop if count limit reached
            if args.count and count >= args.count:
                break
    
    except KeyboardInterrupt:
        print("\nStopped by user", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if input_stream and input_stream != sys.stdin:
            input_stream.close()

if __name__ == "__main__":
    main()
