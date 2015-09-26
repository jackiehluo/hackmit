%Reading in files from the directory
files = dir('./AVIClips05New/training_videos/*.avi');
str = './AVIClips05New/training_videos/';

%create empty feature matrix the size of directory
% Do I need 21 features? 
training_features = zeros(size(files,1),21);

% setting up optical flow
% opticalFlow = vision.OpticalFlow('ReferenceFrameSource', 'Input port');
% opticalFlow.OutputValue = 'Horizontal and vertical components in complex form';

% extract training labels from .txt file
training_labels = [];
train = fopen('Run_train_m.txt','r');
tline = fgets(train);
while ischar(tline)
    line = strsplit(tline);
    training_labels(end+1) = str2double(line(2));
    tline = fgets(train);
end

training_labels = transpose(training_labels);
%%
%extract testing labels from .txt file
testing_labels = [];
test = fopen('Run_test_m.txt', 'r');
tline = fgets(test);
while ischar(tline)
    line = strsplit(tline);
    testing_labels(end+1) = str2double(line(2));
    tline = fgets(test);
end

testing_labels = transpose(testing_labels);
%%
% Initializing the array of objects to contain video properties
list_of_properties(1,size(files,1)) = VideoStats(0);

%% giant for loop to process every element in the directory
fid = fopen('labels.txt', 'wt');

% 
disp('Beginning processing on video files..');
for k = 1:size(files,1)
fprintf('Working on file number %i.\n', k);
    % Read in the video file
    name_of_file = files(k).name;
    strcat(str, name_of_file);
    videoFileReader = VideoReader(name_of_file);
    list_of_properties(k).name = name_of_file;
    fprintf(fid, '%s\n', name_of_file);
    vidWidth = videoFileReader.Width;
    vidHeight = videoFileReader.Height;
    
    % Constructing a movie structure array
    mov = struct('cdata', zeros(vidHeight,vidWidth, 3,'uint8'),...
        'colormap', []);
    
    % Skip one frame at a time until the end of the video is reached
    j = 1;
    
    while hasFrame(videoFileReader)
        mov(j).cdata = readFrame(videoFileReader);
        j = j + 1;
    end
    
    %%
    arrHnnz = [];
    arrVnnz = [];
    avgDistPerFrameX = [];
    avgDistPerFrameY = [];
    
    %% new arrays of stats b/w frames
    zeroHor = [];
    zeroVer = [];
    meanFrames = [];
    medianH = [];
    medianV = [];
    kurtH = [];
    kurtV = [];
    skewH = [];
    skewV = [];
    stdH = [];
    stdV = [];
    
    fprintf('Storing frames in struct for video #%i\n', k);
    
    %initializing optical flow variables
    horizontal_opt_flow = [];
    vertical_opt_flow = [];
    
    skip = 5;
    for i=1:skip:size(mov,2)
        % show the movie frame we just read in
        original_img = mov(i).cdata;
        % skip frames in units of 8 because we know the video rate is 24
        % frames per second
        if i+skip > size(mov,2)
            break;
        end
        % show the next movie frame for comparison
        new_img = mov(i+skip).cdata;
        
        %% Processing for flow detection
        Flow = step(opticalFlow, im2double(rgb2gray(original_img)), ...
            im2double(rgb2gray(new_img)));
        
        %Saving the horizontal and vertical features
        horizontal_opt_flow=real(Flow); 
        vertical_opt_flow=imag(Flow);
%         subplot(2,1,1); imagesc(horizontal_opt_flow+vertical_opt_flow); drawnow;
        arrHnnz(end+1) = nnz(horizontal_opt_flow);
        arrVnnz(end+1) = nnz(vertical_opt_flow);
        
        %% added features %%
        zeroHor(end+1) = sum(horizontal_opt_flow(:) == 0);
        zeroVer(end+1) = sum(vertical_opt_flow(:) ==0);
        
        meanFrames(end+1) = mean(mean(original_img(:,:,1)))-mean(mean(new_img(:,:,1)));
        
        medianH(end+1) = median(horizontal_opt_flow(:));
        medianV(end+1) = median(vertical_opt_flow(:));
        
        skewH(end+1) = skewness(horizontal_opt_flow(:));
        skewV(end+1) = skewness(vertical_opt_flow(:));
        
        kurtH(end+1) = kurtosis(horizontal_opt_flow(:));
        kurtV(end+1) = kurtosis(vertical_opt_flow(:));
        
        stdH(end+1) = std(horizontal_opt_flow(:));
        stdV(end+1) = std(vertical_opt_flow(:));
        
        %% Processing for the detection of SURF features
        ptsOriginalBRISK  = detectBRISKFeatures(original_img(:,:,1), 'MinContrast', 0.01);
        ptsDistortedBRISK = detectBRISKFeatures(new_img(:,:,1), 'MinContrast', 0.01);

        ptsOriginalSURF  = detectSURFFeatures(original_img(:,:,1));
        ptsDistortedSURF = detectSURFFeatures(new_img(:,:,1));
        
        [featuresOriginalFREAK,  validPtsOriginalBRISK]  = extractFeatures(original_img(:,:,1),  ptsOriginalBRISK);
        [featuresDistortedFREAK, validPtsDistortedBRISK] = extractFeatures(new_img(:,:,1), ptsDistortedBRISK);

        [featuresOriginalSURF,  validPtsOriginalSURF]  = extractFeatures(original_img(:,:,1),  ptsOriginalSURF);
        [featuresDistortedSURF, validPtsDistortedSURF] = extractFeatures(new_img(:,:,1), ptsDistortedSURF);

        indexPairsBRISK = matchFeatures(featuresOriginalFREAK, featuresDistortedFREAK, 'MatchThreshold', 40, 'MaxRatio', 0.8);
        indexPairsSURF = matchFeatures(featuresOriginalSURF, featuresDistortedSURF);

        matchedOriginalBRISK  = validPtsOriginalBRISK(indexPairsBRISK(:,1));
        matchedDistortedBRISK = validPtsDistortedBRISK(indexPairsBRISK(:,2));

        matchedOriginalSURF  = validPtsOriginalSURF(indexPairsSURF(:,1));
        matchedDistortedSURF = validPtsDistortedSURF(indexPairsSURF(:,2));
        
        matchedOriginalXY  = [matchedOriginalSURF.Location; matchedOriginalBRISK.Location];
        matchedDistortedXY = [matchedDistortedSURF.Location; matchedDistortedBRISK.Location];
        
        %[tformTotal,inlierDistortedXY,inlierOriginalXY] = estimateGeometricTransform(matchedDistortedXY,matchedOriginalXY,'similarity');
        % figure
        % showMatchedFeatures(original_img,new_img,inlierOriginalXY,inlierDistortedXY)
        % title('Matching points using SURF and BRISK (inliers only)')
        % legend('ptsOriginal','ptsDistorted')

        xVals = abs(matchedOriginalXY(:,1)-matchedDistortedXY(:,1));
        xAvg = mean(xVals);
        yVals = abs(matchedOriginalXY(:,2)-matchedDistortedXY(:,2));
        yAvg = mean(yVals);
        if ~isnan(xAvg) && ~isnan(yAvg)
            avgDistPerFrameX = [avgDistPerFrameX; xAvg];
            avgDistPerFrameY = [avgDistPerFrameY; yAvg];
        end
    end
    %%
%     break;
    training_features(k,:) = [max(avgDistPerFrameX), max(avgDistPerFrameY),...
        min(avgDistPerFrameX), min(avgDistPerFrameY), mean(arrHnnz),mean(arrVnnz),...
        mean(zeroHor), mean(zeroVer), max(zeroHor), max(zeroVer), min(zeroHor), min(zeroVer),...
        mean(meanFrames), mean(medianH), mean(medianV), mean(skewH), mean(skewV), mean(kurtH), mean(kurtV),...
        mean(stdH),mean(stdV)];
    
%     list_of_properties(k).maxX  = max(avgDistPerFrameX);
%     list_of_properties(k).maxY  = max(avgDistPerFrameY);
%     list_of_properties(k).minX  = min(avgDistPerFrameX);
%     list_of_properties(k).minY  = min(avgDistPerFrameY);
%     list_of_properties(k).numberOfFrames = size(mov,2);
%     list_of_properties(k).H = mean(arrHnnz);
%     list_of_properties(k).V = mean(arrVnnz);
    
end

for k=1:size(training_features,2)
    training_features(:,k) = training_features(:,k)/max(abs(training_features(:,k)));
end

fprintf('Training SVM model with default parameters...\n');
model = svmtrain(training_features, training_labels);
%model = svmtrain(training_features(:,:,1,1), training_labels, 'ShowPlot', true);
fprintf('SVM model training complete...\n');

% figure;
% plot(1:size(avgDistPerFrameX,1), avgDistPerFrameX, 1:size(avgDistPerFrameY,1), avgDistPerFrameY)
% legend('X averages over Frame Changes', 'Y averages over Frame Changes')
% % figure;
% plot(1:size(avgDistPerFrameY,1), avgDistPerFrameY)
toc
